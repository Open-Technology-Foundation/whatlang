# DEVELOPMENT GUIDELINES

whatlang 2 is a single C program with an embedded language-ID model. See
`README.md` for usage and `docs/superpowers/specs/2026-11-19-whatlang-c-design.md`
for the design and the bake-off that chose it.

## Layout

| Path | Role |
|------|------|
| `whatlang.c` | The whole program: model mapping, detection, CLI |
| `model/model.bin.xz` | Compressed model (tracked); decompressed to `build/model.bin` |
| `tools/export_model.py` | Regenerates the model from py3langid 0.4.0 |
| `tests/run_tests.sh` | Black-box test suite (Bash, BCS) |
| `tests/fixtures/<code>.txt` | One sample text per language; the filename is the expected code |
| `Makefile` | `build`, `test`, `install`, `uninstall`, `check`, `model`, `clean` (BCS1212) |
| `.bash_completion` | Completion for the CLI flags and `-L` codes |

## Commands

```bash
make build        # build/model.bin + static ./whatlang
make test         # build, then tests/run_tests.sh → "N/N passed"
make clean
shellcheck -x tests/run_tests.sh .bash_completion
```

## Model format

Documented at the top of `tools/export_model.py`. The header magic is
`WLID0002`; `whatlang.c` checks the magic and the exact total size at
start-up. If you change the layout, bump the magic in both files.

Two properties the exporter asserts and the C code relies on:

- The goto edges plus failure links regenerate py3langid's dense DFA exactly.
- Every array is naturally aligned (the `u8` arrays come last).

## Fidelity to py3langid

Behaviour should match `py3langid.langid.LanguageIdentifier(norm_probs=True)`.
Known deliberate differences:

- No features → `und` (py3langid returns an arbitrary label at 1/71).
- No NFC normalisation; all-caps lowering is ASCII only.
- uint8 weights flip about 0.2% of labels, all near-ties.

After changing detection code, re-run a parity check against py3langid on a
few thousand short sentences (Tatoeba per-language exports work well) and
expect at least 99.5% label agreement.

## Code style

- 2-space indentation, no tabs (Makefile recipes excepted).
- C: C11 with GNU extensions, `-Wall -Wextra` clean, no dynamic allocation
  beyond the one feature-count array.
- Bash: BCS; run `shellcheck -x` and a BCS audit on changed scripts.
- Python (exporter only): PEP 8 with 2-space indent, `ruff check` clean.
- Scripts end with `#fin`.
