// whatlang - detect the language of text and print its ISO 639 code.
//
// The model is py3langid 0.4.0 (BSD-3, see LICENSE-py3langid), converted by
// tools/export_model.py and embedded at build time, so the binary needs no
// files at run time. Detection follows py3langid with norm_probs=True:
// Aho-Corasick walk over UTF-8 bytes, naive Bayes over feature counts,
// softmax at temperature sqrt(bytes).
#define _GNU_SOURCE
#include <errno.h>
#include <getopt.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#define VERSION   "2.0.0"
#define MAX_INPUT (64 * 1024)  // bytes examined per input
#define MAX_CLS   256

// exit codes (BCS)
enum { EX_OK = 0, EX_ERR = 1, EX_USAGE = 2, EX_NOENT = 3, EX_IO = 5,
       EX_PERM = 13, EX_INVAL = 22 };

_Static_assert(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__,
               "model layout is little-endian");

#ifndef MODEL_PATH
#define MODEL_PATH "build/model.bin"
#endif
__asm__(".section .rodata\n.balign 16\n.globl wl_model\nwl_model:\n"
        ".incbin \"" MODEL_PATH "\"\n.globl wl_model_end\nwl_model_end:\n"
        ".previous\n");
extern const unsigned char wl_model[], wl_model_end[];

typedef struct {
  char magic[8];
  uint32_t n_states, n_edges, n_feat, n_cls;
  float lo, step;
} model_hdr;

static const model_hdr *H;
static const char *NAMES;          // n_cls x 4 bytes, NUL-terminated codes
static const uint32_t *START, *FAIL, *EV;
static const int32_t *OUT;
static const float *PC;
static const uint8_t *EB, *PTC;
static uint32_t ROOT[256];         // dense goto row for state 0

static uint32_t *CNT;              // per-feature hit counts, reset after use
static uint32_t SEEN[MAX_INPUT];   // features hit, in first-seen order

static void die(int code, const char *msg) {
  fprintf(stderr, "whatlang: %s\n", msg);
  exit(code);
}

// Map the embedded model; refuse anything whose size doesn't add up.
static void model_load(void) {
  const unsigned char *p = wl_model;
  size_t size = (size_t)(wl_model_end - wl_model);
  if (size < sizeof *H) die(EX_ERR, "embedded model is truncated");
  H = (const model_hdr *)p;
  if (memcmp(H->magic, "WLID0002", 8)) die(EX_ERR, "embedded model has wrong format");
  if (H->n_cls == 0 || H->n_cls > MAX_CLS) die(EX_ERR, "embedded model is corrupt");

  size_t ns = H->n_states, ne = H->n_edges, nf = H->n_feat, nc = H->n_cls;
  size_t want = sizeof *H + 4 * nc + 4 * (ns + 1) + 4 * ns + 4 * ns + 4 * ne
                + 4 * nc + ne + nf * nc;
  if (size != want) die(EX_ERR, "embedded model size mismatch");

  p += sizeof *H;
  NAMES = (const char *)p;      p += 4 * nc;
  START = (const uint32_t *)p;  p += 4 * (ns + 1);
  FAIL = (const uint32_t *)p;   p += 4 * ns;
  OUT = (const int32_t *)p;     p += 4 * ns;
  EV = (const uint32_t *)p;     p += 4 * ne;
  PC = (const float *)p;        p += 4 * nc;
  EB = p;                       p += ne;
  PTC = p;

  for (uint32_t e = START[0]; e < START[1]; e++) ROOT[EB[e]] = EV[e];
  CNT = calloc(nf, sizeof *CNT);
  if (!CNT) die(EX_ERR, "out of memory");
}

static const char *lang_name(uint32_t c) { return NAMES + 4 * c; }

// Child of state s on byte b, or 0 if none (children are sorted by byte).
static uint32_t go_child(uint32_t s, uint8_t b) {
  uint32_t lo = START[s], hi = START[s + 1], end = hi;
  while (lo < hi) {
    uint32_t mid = (lo + hi) >> 1;
    if (EB[mid] < b) lo = mid + 1; else hi = mid;
  }
  return (lo < end && EB[lo] == b) ? EV[lo] : 0;
}

// Fill allow[] from a comma-separated list; NULL or empty allows all.
// Returns EX_OK or EX_INVAL (after reporting the unknown code).
static int parse_langs(const char *list, unsigned char *allow) {
  int any = 0;
  memset(allow, 0, MAX_CLS);
  for (const char *p = list ? list : ""; *p;) {
    size_t len = strcspn(p, ",");
    if (len) {
      int found = 0;
      for (uint32_t c = 0; c < H->n_cls; c++)
        if (strlen(lang_name(c)) == len && !strncmp(p, lang_name(c), len))
          allow[c] = 1, found = 1;  // aliases (sr, uz) share a code
      if (!found) {
        fprintf(stderr, "whatlang: unknown language code '%.*s' (see whatlang -l)\n",
                (int)len, p);
        return EX_INVAL;
      }
      any = 1;
    }
    p += len + (p[len] == ',');
  }
  if (!any) memset(allow, 1, H->n_cls);
  return EX_OK;
}

// Drop an incomplete UTF-8 sequence cut off at the end of the buffer.
static size_t trim_utf8(const unsigned char *buf, size_t n) {
  size_t j = n;
  while (j > 0 && n - j < 3 && (buf[j - 1] & 0xC0) == 0x80) j--;
  if (j == 0) return n;
  unsigned char lead = buf[j - 1];
  size_t need = lead >= 0xF0 ? 4 : lead >= 0xE0 ? 3 : lead >= 0xC0 ? 2 : 1;
  return (need > 1 && n - (j - 1) < need) ? j - 1 : n;
}

// py3langid lowercases all-caps text; this is its ASCII approximation.
static void lower_if_allcaps(unsigned char *buf, size_t n) {
  int lower = 0, upper = 0;
  for (size_t i = 0; i < n; i++) {
    lower |= buf[i] >= 'a' && buf[i] <= 'z';
    upper |= buf[i] >= 'A' && buf[i] <= 'Z';
  }
  if (upper && !lower)
    for (size_t i = 0; i < n; i++)
      if (buf[i] >= 'A' && buf[i] <= 'Z') buf[i] += 'a' - 'A';
}

// Classify n bytes; returns the code and sets *conf. "und" if no features.
static const char *detect(unsigned char *buf, size_t n,
                          const unsigned char *allow, double *conf) {
  n = trim_utf8(buf, n);
  lower_if_allcaps(buf, n);

  size_t nseen = 0;
  uint32_t s = 0;
  for (size_t i = 0; i < n; i++) {
    uint8_t b = buf[i];
    uint32_t t = 0;
    while (s && !(t = go_child(s, b))) s = FAIL[s];
    s = s ? t : ROOT[b];
    int32_t f = OUT[s];
    if (f >= 0 && !CNT[f]++) SEEN[nseen++] = (uint32_t)f;
  }
  *conf = 0;
  if (!nseen) return "und";

  uint32_t nc = H->n_cls;
  double score[MAX_CLS], wsum = 0;
  for (uint32_t c = 0; c < nc; c++) score[c] = 0;
  for (size_t k = 0; k < nseen; k++) {
    uint32_t f = SEEN[k];
    double w = log1p(CNT[f]);
    const uint8_t *row = PTC + (size_t)f * nc;
    for (uint32_t c = 0; c < nc; c++) score[c] += w * row[c];
    wsum += w;
    CNT[f] = 0;
  }

  // dequantise (lo + step*q), then softmax over allowed classes
  double inv_t = 1.0 / sqrt((double)n), max = -INFINITY, z = 0;
  for (uint32_t c = 0; c < nc; c++) {
    score[c] = PC[c] + wsum * H->lo + H->step * score[c];
    if (allow[c] && score[c] > max) max = score[c];
  }
  double prob[MAX_CLS] = {0};
  for (uint32_t c = 0; c < nc; c++)
    if (allow[c]) z += prob[c] = exp((score[c] - max) * inv_t);

  // fold alias columns into their first occurrence, then take the best
  int best = -1;
  for (uint32_t c = 0; c < nc; c++) {
    if (!allow[c]) continue;
    prob[c] /= z;
    for (uint32_t d = 0; d < c; d++)
      if (allow[d] && !strcmp(lang_name(c), lang_name(d))) {
        prob[d] += prob[c];
        prob[c] = 0;
        break;
      }
  }
  for (uint32_t c = 0; c < nc; c++)
    if (allow[c] && (best < 0 || prob[c] > prob[best])) best = (int)c;
  *conf = prob[best];
  return lang_name((uint32_t)best);
}

// Read up to MAX_INPUT bytes; returns -1 on read error (errno set).
static long read_input(FILE *fp, unsigned char *buf) {
  size_t n = 0, got;
  while (n < MAX_INPUT && (got = fread(buf + n, 1, MAX_INPUT - n, fp)) > 0) n += got;
  return ferror(fp) ? -1 : (long)n;
}

// Consume the rest of a pipe so the writer doesn't die of SIGPIPE, which
// would fail a 'set -o pipefail' caller. Regular files need no draining.
static void drain(FILE *fp) {
  struct stat st;
  static unsigned char sink[1 << 16];
  if (fstat(fileno(fp), &st) == 0 && S_ISREG(st.st_mode)) return;
  while (fread(sink, 1, sizeof sink, fp) > 0) {}
}

static int errno_exit(int err) {
  return err == ENOENT ? EX_NOENT : (err == EACCES || err == EPERM) ? EX_PERM : EX_IO;
}

// Classify one named input ("-" is stdin) and print the result line.
static int process(const char *path, int show_name, int show_conf,
                   const unsigned char *allow) {
  static unsigned char buf[MAX_INPUT];
  int is_stdin = !strcmp(path, "-");
  FILE *fp = is_stdin ? stdin : fopen(path, "rb");
  if (!fp) {
    int err = errno;
    fprintf(stderr, "whatlang: %s: %s\n", path, strerror(err));
    return errno_exit(err);
  }
  long n = read_input(fp, buf);
  int err = errno;
  if (is_stdin && n == MAX_INPUT) drain(fp);
  if (!is_stdin) fclose(fp);
  if (n < 0) {
    fprintf(stderr, "whatlang: %s: %s\n", path, strerror(err));
    return errno_exit(err);
  }

  double conf;
  const char *code = detect(buf, (size_t)n, allow, &conf);
  if (show_name) printf("%s\t", path);
  if (show_conf) printf("%s\t%.2f\n", code, conf); else puts(code);
  return EX_OK;
}

static void usage(void) {
  fputs(
    "Usage: whatlang [OPTIONS] [FILE...]\n"
    "Detect the language of text and print its ISO 639 code.\n"
    "Reads stdin when no FILE is given, or for '-'. Only the first 64 KiB\n"
    "of each input is examined.\n"
    "\n"
    "  -c, --confidence   append TAB and a confidence from 0.00 to 1.00\n"
    "  -L, --langs LIST   only consider these comma-separated codes, e.g. id,en\n"
    "                     (default: $WHATLANG_LANGS, else all languages)\n"
    "  -l, --list         list supported language codes\n"
    "  -V, --version      print version\n"
    "  -h, --help         show this help\n"
    "\n"
    "Prints 'und' when the text has no detectable features. With several\n"
    "files each line is FILE<TAB>CODE.\n"
    "\n"
    "Exit status: 0 ok, 2 usage error, 3 file not found, 5 I/O error,\n"
    "13 permission denied, 22 unknown language code.\n", stdout);
}

int main(int argc, char **argv) {
  static const struct option opts[] = {
    {"confidence", no_argument, 0, 'c'},
    {"langs", required_argument, 0, 'L'},
    {"list", no_argument, 0, 'l'},
    {"version", no_argument, 0, 'V'},
    {"help", no_argument, 0, 'h'},
    {0, 0, 0, 0},
  };
  int show_conf = 0, list = 0, opt;
  const char *langs = getenv("WHATLANG_LANGS");

  while ((opt = getopt_long(argc, argv, "cL:lVh", opts, NULL)) != -1) {
    switch (opt) {
      case 'c': show_conf = 1; break;
      case 'L': langs = optarg; break;
      case 'l': list = 1; break;
      case 'V': puts("whatlang " VERSION); return EX_OK;
      case 'h': usage(); return EX_OK;
      default:
        fputs("Try 'whatlang --help' for more information.\n", stderr);
        return EX_USAGE;
    }
  }

  model_load();
  if (list) {
    for (uint32_t c = 0; c < H->n_cls; c++) {
      uint32_t d = 0;
      while (d < c && strcmp(lang_name(c), lang_name(d))) d++;
      if (d == c) puts(lang_name(c));
    }
    return EX_OK;
  }

  unsigned char allow[MAX_CLS];
  int rc = parse_langs(langs, allow);
  if (rc) return rc;

  int nfiles = argc - optind;
  if (nfiles == 0) rc = process("-", 0, show_conf, allow);
  for (int i = optind; i < argc; i++) {
    int r = process(argv[i], nfiles > 1, show_conf, allow);
    if (r && !rc) rc = r;
  }
  if (fflush(stdout) || ferror(stdout)) die(EX_IO, "write error");
  return rc;
}
