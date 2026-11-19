# whatlang 2.0 — C rewrite: design

Date: 2026-11-19. Status: approved.

## Intent

A superfast, portable routine that takes a piece of text and returns a
language code, callable from Bash scripts on any host without a Python
environment. No LLM calls.

whatlang 1.x (Python + langdetect) was slow (~200 ms per call), confidently
wrong on short text (`apa kabar` → Tagalog at 1.00), and broken (its venv
had lost its dependencies). It has no callers.

## Goals

- One self-contained static binary; deploys by copying a single file.
- About 1 ms per call including process start.
- Accurate on short text, especially Indonesian and English.
- Optional restriction to a language set, applied *during* scoring.

## Non-goals and anti-goals

- No LLM fallback. Tested: the local gemma3-4b language model was slower
  (~235 ms warm, 22 s cold) and no more accurate on short Indonesian.
- No compatibility with the 1.x CLI or output format.
- No Python runtime dependency for using the tool (Python is only needed to
  regenerate the model).
- Failure: any build that needs a venv, network, or data files beside the
  binary at run time.

## Approaches considered

| Approach | Trade-off | Outcome |
|---|---|---|
| C port of py3langid's model, embedded in a static binary | ~0.8 ms/call, no deps, 16.8 MB binary; model is BSD-3 | **Chosen** |
| Swap langdetect for a Python library (py3langid, lingua) | Least work, but Python start-up (~25 ms+) and venv portability | Rejected |
| Own n-gram routine trained for a few languages | Smallest, but needs training data and loses broad coverage | Rejected |
| fastText lid.176 compressed model in C | 1 MB model, but Malay 23% / Indonesian 86% in testing, CC-BY-SA | Rejected |

Bake-off (6,000 Tatoeba sentences, 10 languages, plus 21 hand-written
id/en business phrases): py3langid was best on short text (89.4% for
≤20 chars). Restricted to `id,en` it scored 100% on ≤20-char sentences.
The C port agrees with py3langid on 99.8% of labels at equal accuracy.

## Design

### Model

- Source: py3langid 0.4.0 (`model.npz.xz`, 142 classes / 140 language codes, BSD-3).
- `tools/export_model.py` converts it to a flat little-endian binary:
  - The dense Aho-Corasick DFA (104,583 states × 256) becomes trie goto edges
    (CSR, sorted by byte) plus failure links. The exporter regenerates the
    dense table from them and asserts exact equality.
  - `nb_ptc` (100,053 features × 142 classes) is quantised linearly to uint8.
  - Arrays are ordered so every one is naturally aligned.
- The repo carries `model/model.bin.xz` (~3.5 MB). `make` decompresses it to
  `build/model.bin` and embeds it with `.incbin`.

### Detection (matches py3langid with `norm_probs=True`)

1. Read up to 64 KiB of input; trim a trailing partial UTF-8 sequence.
2. Lowercase if the text is all caps (ASCII approximation of `str.isupper`).
   No NFC normalisation, a documented difference from py3langid.
3. Walk the automaton byte by byte; count feature hits.
4. Score: `pc[c] + Σ log1p(count_f) · ptc[f, c]` over allowed classes.
5. Softmax at temperature `sqrt(bytes)`; fold duplicate labels (`sr`, `uz`).
6. No features at all → `und`.

### CLI

```
whatlang [-c] [-L LANGS] [FILE...]
  -c, --confidence   append TAB + confidence (0.00–1.00)
  -L, --langs LIST   restrict to comma-separated codes (default: $WHATLANG_LANGS, else all)
  -l, --list         list supported codes
  -V, --version      print version
  -h, --help         usage
```

- No FILE, or `-`, reads stdin.
- Output is the code alone; with several files each line is `FILE<TAB>code`.
- Exit codes (BCS): 0 success (including `und`), 2 usage, 3 file not found,
  5 I/O error, 22 invalid argument (unknown language code).

### Repository layout

```
whatlang.c              source
Makefile                build, test, install (BCS1212)
model/model.bin.xz      compressed model
tools/export_model.py   regenerate model from py3langid
tests/run_tests.sh      test suite (Bash)
tests/fixtures/         sample texts, one per language
.bash_completion        completion for the new flags
README.md, DEVELOPMENT.md, LICENSE, LICENSE-py3langid
```

Everything from 1.x is removed: Python code, venvs, pytest suite,
`setup.py`, `requirements.txt`, `install.sh`, caches, and stale configs.
Sample texts move to `tests/fixtures/`.

## Decided calls

- Name and symlink stay `whatlang`.
- No default restriction and no automatic ms→id folding; `WHATLANG_LANGS`
  provides a per-environment default.
- The built binary and `build/` are git-ignored; the compressed model is tracked.

## Left to the builder

- Help text wording, test case selection, Makefile details within BCS1212.
