# whatlang 2.0 C Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Python whatlang with a static C binary that embeds py3langid's model and prints a language code in about 1 ms.

**Architecture:** A Python exporter converts py3langid's model to a compact aligned binary (trie + fail links, uint8 scores), shipped xz-compressed. `make` decompresses it and embeds it into `whatlang.c` via `.incbin`, producing one static executable.

**Tech Stack:** C (gcc 13, glibc static, `-lm`), GNU make, xz, Bash 5.2 test suite; Python 3.12 + py3langid 0.4.0 + numpy only for regenerating the model.

**Spec:** `docs/superpowers/specs/2026-11-19-whatlang-c-design.md`

## Global Constraints

- 2-space indentation everywhere, no tabs (except Makefile recipe lines, which make requires).
- Static binary; no files read at run time other than the input.
- Input cap 64 KiB; output the code alone; `und` when no features.
- Exit codes: 0 success (incl. `und`), 2 usage, 3 file not found, 5 I/O error, 22 unknown language code.
- `-L` restricts during scoring; default from `WHATLANG_LANGS`; no ms→id folding.
- Bash files pass `shellcheck -x` and the `bcscheck` skill; scripts end with `#fin`.
- Makefile follows BCS1212: `all` → `help`; targets install, uninstall, check, test, help; `srcdir`-anchored sources.
- Public repo: no internal hostnames or IPs in any tracked file.

## Review Focus

1. Input with no letters (digits, punctuation, whitespace) → `und` or `zxx`, exit 0, no crash.
2. Input longer than 64 KiB, or cut mid-UTF-8 character → still classifies, no read past buffer.
3. `-L` with an unknown or empty code (`-L xx`, `-L id,,en`) → exit 22 with a message naming the code; empty items ignored.
4. Unreadable or missing FILE among several → message on stderr, the other files still reported, exit 3.
5. Binary (non-text) input such as `/bin/ls` → a code is printed, no crash.

Each has a test in Task 2.

---

### Task 1: Model exporter and compressed model

**Files:**
- Create: `tools/export_model.py`, `model/model.bin.xz`, `LICENSE-py3langid`

**Interfaces:**
- Produces: binary layout, little-endian, every array naturally aligned:
  header `<8sIIIIff>` = magic `WLID0002`, n_states, n_edges, n_feat, n_cls, lo, step (32 bytes);
  then `names[n_cls][4]` (NUL-padded), `start[n_states+1] u32`, `fail[n_states] u32`,
  `out[n_states] i32`, `ev[n_edges] u32`, `pc[n_cls] f32`, `eb[n_edges] u8`,
  `ptc[n_feat][n_cls] u8`. Score value = `lo + step * q`.

- [ ] **Step 1:** Port the spike exporter, with the array order above (pc before eb, so all arrays are aligned) and magic `WLID0002`. Keep the exact-regeneration assert of the dense DFA.
- [ ] **Step 2:** Run `python3 -I tools/export_model.py build/model.bin` in a venv with py3langid 0.4.0. Expected stderr: `DFA verified: 104583 states, 104582 edges`.
- [ ] **Step 3:** `xz -9e -c build/model.bin > model/model.bin.xz` (about 3.5 MB). Add `LICENSE-py3langid` (BSD-3 text from the py3langid dist-info).

### Task 2: whatlang.c, Makefile and test suite

**Files:**
- Create: `whatlang.c`, `Makefile`, `tests/run_tests.sh`, `tests/fixtures/<code>.txt` (moved from `test.*.txt`)

**Interfaces:**
- Consumes: `model/model.bin.xz` layout from Task 1.
- Produces: `whatlang` binary; `make build`, `make test`, `make install|uninstall|check|help|clean`.

- [ ] **Step 1: Write `tests/run_tests.sh` first.** It takes the binary path (default `./whatlang`), counts pass and fail, prints `N/M passed`, and exits 1 on any failure. Cases:
  - Each fixture `tests/fixtures/<code>.txt` → `<code>`; `zh-tw` expects `zh`; `elvish` is excluded.
  - With `-L id,en`: `apa kabar`, `terima kasih`, `selamat pagi pak`, `mohon dicek ya`, `baik pak` → `id`; `good morning`, `please find attached` → `en`.
  - Unrestricted: `apa kabar` → `id`; `Bonjour tout le monde, comment allez-vous` → `fr`; `こんにちは世界` → `ja`.
  - Empty stdin → `und`, exit 0. `12345` → exit 0, output in {`und`,`zxx`}.
  - `-c` output matches `^[a-z]{2,3}\t[01]\.[0-9]{2}$`.
  - `WHATLANG_LANGS=id,en` + `Bonjour tout le monde` → `en` or `id` (never `fr`); `-L ''` overrides it back to all languages → `fr`.
  - Two files → two lines `FILE\tcode`; a missing file among them → its error on stderr, the other line still printed, exit 3.
  - `-L xx` → exit 22, stderr contains `xx`. `-L id,,en` → exit 0. `-Z` → exit 2.
  - 200 KiB fixture input (repeated) → `id`; input ending in a truncated multi-byte char → exit 0.
  - `/bin/ls` as input → exit 0.
  - `-l` lists at least 140 lines, including `id`, `ms` and `en`; `-V` prints `whatlang 2.0.0`.
- [ ] **Step 2:** `make test` with no binary → fails (build target missing).
- [ ] **Step 3: Write the Makefile.** `build/model.bin: model/model.bin.xz` (`xz -dc`); `whatlang: whatlang.c build/model.bin` → `$(CC) -O2 -Wall -Wextra -static -DMODEL_PATH='"build/model.bin"' -o $@ whatlang.c -lm`; `test: whatlang`. `install` installs the binary plus `.bash_completion` per BCS1212, then runs `check` unless `DESTDIR` is set.
- [ ] **Step 4: Write `whatlang.c`** from the spike, with these changes:
  - `getopt_long`: `-c/--confidence`, `-L/--langs`, `-l/--list`, `-V/--version`, `-h/--help`.
  - `WHATLANG_LANGS` is read when `-L` is absent; codes are validated against the model.
  - Files are processed in turn; feature counts reset via the `seen` list, not by re-zeroing all `n_feat` slots.
  - Trailing partial UTF-8 is trimmed; the input is read up to 64 KiB, and the rest of the stream is not consumed.
  - Endianness is guarded with `_Static_assert(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__)`, and the model magic is checked.
  - `#define VERSION "2.0.0"`.
- [ ] **Step 5:** `make test` → `N/N passed`. Spot-check parity: run the scratch parity script against the new binary; expect ≥99.5% agreement with py3langid.

### Task 3: Remove 1.x and rewrite the docs

**Files:**
- Delete: `whatlang.py`, the old `whatlang` wrapper (replaced by the build output), `setup.py`, `requirements.txt`, `pytest.ini`, `test_module.py`, `install.sh`, `tests/*.py`, `tests/README.md`, `tests/__pycache__`, `__pycache__`, `.pytest_cache`, `.coverage`, `.venv`, `test_venv`, `.claude/settings.local.json` (1.x permissions only), `/etc/default/whatlang_config.json` (2023 leftover config from an earlier version).
- Rewrite: `README.md`, `DEVELOPMENT.md` (target of the `CLAUDE.md` symlink), `.bash_completion`, `.gitignore`.
- Modify: `../README.md` (whatlang section and table row), `../CLAUDE.md` (install line, `requirements.txt` note).

- [ ] **Step 1:** `git rm` the tracked 1.x files and `git mv test.*.txt tests/fixtures/`; `rm -rf` the untracked caches and venvs; remove the `/etc/default` file.
- [ ] **Step 2:** Rewrite the docs for the 2.0 CLI. Completion covers the five flags and offers `-L` codes from `whatlang -l`. `.gitignore` covers `/whatlang`, `build/`, `CLAUDE.md`, `.claude/`, `.gudang/`, and editor junk.
- [ ] **Step 3:** `rg -n -i 'langdetect|pycountry|chardet|venv|pytest|whatlang\.py|install\.sh|--format' .. --glob '!**/docs/superpowers/**'` within `Trans/` → no whatlang hits.
- [ ] **Step 4:** `shellcheck -x tests/run_tests.sh .bash_completion` is clean; `bcscheck` skill is PASS on both; `make test` still `N/N`; `whatlang` on PATH (existing `/usr/local/bin` symlink) answers `apa kabar` → `id`.
