#!/usr/bin/bash
#shellcheck disable=SC2015  # BCS idiom: cond && pass || fail; pass() always returns 0
# run_tests.sh - black-box test suite for the whatlang binary
#   Usage: tests/run_tests.sh [PATH_TO_WHATLANG]
set -euo pipefail
shopt -s inherit_errexit nullglob
declare -rx PATH=/usr/local/bin:/usr/bin:/bin

#shellcheck disable=SC2155  # accepted: declare masks realpath's exit status (BCS0103)
declare -r SCRIPT_PATH=$(realpath -- "$0")
declare -r SCRIPT_DIR=${SCRIPT_PATH%/*}
declare -r FIXTURES="$SCRIPT_DIR"/fixtures

declare -- BIN=${1:-"$SCRIPT_DIR"/../whatlang}
declare -i PASS=0 FAIL=0
declare -- TMPDIR_T=''

cleanup() {
  [[ -n $TMPDIR_T ]] && rm -rf -- "$TMPDIR_T" ||:
}
trap cleanup EXIT

pass() { PASS+=1; }
fail() { FAIL+=1; printf 'FAIL: %s\n' "$*" >&2; }

# expect_out NAME EXPECTED_OUTPUT INPUT [ARGS...]: stdout must equal EXPECTED
expect_out() {
  local -- name=$1 want=$2 input=$3 got
  shift 3
  got=$(printf '%s' "$input" | "$BIN" "$@" 2>/dev/null) ||:
  [[ $got == "$want" ]] && pass || fail "$name: want ${want@Q}, got ${got@Q}"
}

# expect_rc NAME EXPECTED_RC INPUT [ARGS...]: exit status must equal EXPECTED_RC
expect_rc() {
  local -- name=$1 input=$3
  local -i want=$2 rc=0
  shift 3
  printf '%s' "$input" | "$BIN" "$@" >/dev/null 2>&1 || rc=$?
  ((rc == want)) && pass || fail "$name: want exit $want, got $rc"
}

test_fixtures() {
  local -- f code want
  for f in "$FIXTURES"/*.txt; do
    code=${f##*/}; code=${code%.txt}
    [[ $code == elvish ]] && continue
    want=${code%%-*}
    expect_out "fixture $code" "$want" "$(<"$f")"
  done
  # an invented language must still produce a code, not an error
  expect_rc 'fixture elvish runs' 0 "$(<"$FIXTURES"/elvish.txt)"
}

test_short_text() {
  local -- s
  for s in 'apa kabar' 'terima kasih' 'selamat pagi pak' 'mohon dicek ya' 'baik pak'; do
    expect_out "-L id,en ${s@Q}" id "$s" -L id,en
  done
  for s in 'good morning' 'please find attached'; do
    expect_out "-L id,en ${s@Q}" en "$s" -L id,en
  done
  expect_out 'apa kabar unrestricted' id 'apa kabar'
  expect_out 'french sentence' fr 'Bonjour tout le monde, comment allez-vous'
  expect_out 'japanese' ja 'こんにちは世界'
}

test_edge_input() {
  local -- got
  expect_out 'empty stdin' und ''
  expect_rc 'empty stdin rc' 0 ''
  got=$(printf '12345' | "$BIN") ||:
  [[ $got == und || $got == zxx ]] && pass || fail "digits: got ${got@Q}"
  expect_rc 'digits rc' 0 '12345'
  expect_rc 'whitespace only' 0 $'  \n\t '

  got=$(printf 'terima kasih banyak' | "$BIN" -c) ||:
  [[ $got =~ ^[a-z]{2,3}$'\t'[01]\.[0-9]{2}$ ]] && pass || fail "-c format: got ${got@Q}"

  # input far beyond the 64 KiB cap
  local -- big='' id_text
  id_text=$(<"$FIXTURES"/id.txt)
  while ((${#big} < 200000)); do big+="$id_text "; done
  expect_out '200 KiB input' id "$big"
  # the writer must not die of SIGPIPE: callers use pipefail
  local -i rc=0
  printf '%s' "$big" | "$BIN" >/dev/null || rc=$?
  ((rc == 0)) && pass || fail "200 KiB piped input: pipeline exit $rc"

  # truncated multi-byte character at end of input
  got=$(printf 'Selamat datang di Indonesia \xe3\x81' | "$BIN") ||:
  [[ $got == id || $got == ms ]] && pass || fail "truncated utf-8: got ${got@Q}"

  rc=0
  "$BIN" /bin/ls >/dev/null 2>&1 || rc=$?
  ((rc == 0)) && pass || fail "binary input: exit $rc"
}

test_lang_set() {
  local -- got
  got=$(printf 'Bonjour tout le monde' | WHATLANG_LANGS=id,en "$BIN") ||:
  [[ $got == en || $got == id ]] && pass || fail "WHATLANG_LANGS: got ${got@Q}"
  got=$(printf 'Bonjour tout le monde' | WHATLANG_LANGS=id,en "$BIN" -L '') ||:
  [[ $got == fr ]] && pass || fail "-L '' overrides env: got ${got@Q}"

  expect_rc '-L unknown code' 22 'hello world' -L xx
  got=$(printf 'hello' | "$BIN" -L id,xx 2>&1 >/dev/null) ||:
  [[ $got == *xx* ]] && pass || fail "-L xx message: got ${got@Q}"
  expect_rc '-L empty item' 0 'hello world' -L id,,en
  expect_rc 'bad option' 2 'hello' -Z
}

test_files() {
  local -- out err
  local -i rc=0
  TMPDIR_T=$(mktemp -d) || { printf 'mktemp -d failed\n' >&2; exit 1; }
  cp -- "$FIXTURES"/id.txt "$FIXTURES"/en.txt "$TMPDIR_T"/ \
    || { printf 'cannot copy fixtures to %s\n' "$TMPDIR_T" >&2; exit 1; }

  out=$("$BIN" -- "$FIXTURES"/fr.txt) ||:
  [[ $out == fr ]] && pass || fail "single file: got ${out@Q}"

  out=$(cd -- "$TMPDIR_T" && "$BIN" id.txt en.txt) ||:
  [[ $out == $'id.txt\tid\nen.txt\ten' ]] && pass || fail "two files: got ${out@Q}"

  out=$(cd -- "$TMPDIR_T" && "$BIN" id.txt missing.txt en.txt 2>"$TMPDIR_T"/err) || rc=$?
  err=$(<"$TMPDIR_T"/err)
  [[ $out == $'id.txt\tid\nen.txt\ten' ]] && pass || fail "missing file, others: got ${out@Q}"
  [[ $err == *missing.txt* ]] && pass || fail "missing file message: got ${err@Q}"
  ((rc == 3)) && pass || fail "missing file rc: want 3, got $rc"

  out=$(printf 'apa kabar' | "$BIN" -L id,en -) ||:
  [[ $out == id ]] && pass || fail "dash reads stdin: got ${out@Q}"
}

test_info() {
  local -- list ver
  list=$("$BIN" -l) ||:
  (($(wc -l <<<"$list") >= 140)) && pass || fail '-l lists >= 140 codes'
  [[ $'\n'$list$'\n' == *$'\nid\n'* && $'\n'$list$'\n' == *$'\nms\n'* \
     && $'\n'$list$'\n' == *$'\nen\n'* ]] && pass || fail '-l includes id, ms, en'
  ver=$("$BIN" -V) ||:
  [[ $ver == 'whatlang 2.0.0' ]] && pass || fail "-V: got ${ver@Q}"
  "$BIN" -h | grep -q -- '--langs' && pass || fail '-h mentions --langs'
}

main() {
  [[ -x $BIN ]] || { printf 'whatlang binary not found: %s\n' "$BIN" >&2; exit 3; }
  test_fixtures
  test_short_text
  test_edge_input
  test_lang_set
  test_files
  test_info
  printf '%d/%d passed\n' "$PASS" $((PASS + FAIL))
  ((FAIL == 0))
}

main "$@"
#fin
