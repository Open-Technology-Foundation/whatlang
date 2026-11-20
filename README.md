# whatlang

Detect the language of a piece of text and print its ISO 639 code. One
static binary, no runtime dependencies, about 1 ms per call.

```bash
$ echo 'apa kabar' | whatlang
id
$ whatlang -c report.txt
en	0.98
```

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Install

Needs gcc, GNU make, xz and a static libc (`libc6-dev` on Ubuntu).

```bash
git clone https://github.com/Open-Technology-Foundation/whatlang
cd whatlang
make build
make test
sudo make install        # /usr/local/bin/whatlang + bash completion
```

The result is a single self-contained file, so deploying to another
x86-64 Linux host is just copying `whatlang`.

## Usage

```
whatlang [OPTIONS] [FILE...]

  -c, --confidence   append TAB and a confidence from 0.00 to 1.00
  -L, --langs LIST   only consider these comma-separated codes, e.g. id,en
                     (case and blanks ignored; default: $WHATLANG_LANGS,
                     else all languages)
  -l, --list         list supported language codes
  -V, --version      print version
  -h, --help         show this help
```

- Reads stdin when no FILE is given, or for `-`.
- Only the first 64 KiB of each input is examined.
- Prints `und` when the text has no detectable features (empty, or words the
  model has no n-grams for) and `zxx` for text with no linguistic content.
- With several files each line is `FILE<TAB>CODE`.

### Restricting the language set

Short text is where language detectors fail, and most of the failures are
between closely related languages. If you know the candidates, say so: the
restriction is applied while scoring, so the best of the allowed languages
wins.

```bash
$ echo 'selamat pagi pak' | whatlang
ms
$ echo 'selamat pagi pak' | whatlang -L id,en
id
$ export WHATLANG_LANGS=id,en      # default for every call in this shell
```

`-L ''` clears a `WHATLANG_LANGS` default for one call.

### In scripts

```bash
lang=$(whatlang -- "$file")
if [[ $lang == id ]]; then ...; fi

# with a confidence threshold
read -r lang conf < <(whatlang -c -- "$file")
if [[ $conf < 0.70 ]]; then lang=und; fi
```

### Exit status

| Code | Meaning |
|------|---------|
| 0 | success (including `und`) |
| 2 | usage error |
| 3 | file not found |
| 5 | I/O error |
| 13 | permission denied |
| 22 | unknown language code in `-L` / `WHATLANG_LANGS` |

With several files, one failing file does not stop the others; the exit
status is that of the first failure.

## Accuracy and speed

Measured on 6,000 Tatoeba sentences in 10 languages:

| | ≤20 chars | all | per call |
|---|---|---|---|
| whatlang 2 | 89% | 93% | ~0.8 ms (whole process) |
| whatlang 2, `-L` to the 10 test languages | 97% | 96% | |
| whatlang 2, `-L id,en` on id/en text | 100% | 99.9% | |
| whatlang 1 (Python, langdetect) | 75% | 80% | ~200 ms |

Confidence is calibrated enough to act on: without `-L`, a threshold of
0.70 flags about 93% of wrong answers along with about 20% of right ones.

## How it works

The model is [py3langid](https://github.com/adbar/py3langid) 0.4.0, a naive
Bayes classifier over byte n-grams covering 140 languages. A byte-level
Aho-Corasick automaton picks out the n-gram features; each language's score
is its prior plus the sum of `log1p(count) × weight` over the features found;
a softmax at temperature `sqrt(bytes)` turns scores into a confidence.

`tools/export_model.py` converts py3langid's model into a compact binary:
the dense 39 MB automaton becomes trie edges plus failure links (1.8 MB,
verified to reproduce the original exactly), and weights are quantised to one
byte. The result is stored xz-compressed in `model/model.bin.xz` and embedded
in the binary at build time. Labels agree with py3langid on 99.8% of the test
sentences, and the differences are near-ties.

To regenerate the model after a py3langid update:

```bash
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install py3langid==0.4.0 numpy
PATH=/tmp/venv/bin:$PATH make model build test
```

## Limitations

- Indonesian and Malay are hard to tell apart on short text; use `-L`.
- No Unicode normalisation (py3langid applies NFC), and only ASCII all-caps
  text is lowercased. Decomposed (NFD) text and all-caps Cyrillic or Greek can
  be misdetected; lowercase or NFC-normalise such input first.
- The binary is built for the host architecture and assumes a little-endian
  CPU.

## Licence

GPL-3.0 (`LICENSE`). The embedded model is from py3langid, BSD-3-Clause
(`LICENSE-py3langid`).
