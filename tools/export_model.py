#!/usr/bin/env python3
"""Export py3langid's model to the flat binary embedded in whatlang.

Usage: export_model.py OUTPUT.bin   (needs py3langid 0.4.0 and numpy)

py3langid stores its feature scanner as a dense Aho-Corasick DFA
(states x 256, ~39 MB). We recover the trie (goto edges) plus failure
links, assert they regenerate the dense DFA exactly, and store goto/fail
in CSR form (~1.8 MB). nb_ptc is quantised linearly to uint8, which
changes ~0.2% of labels, all near-ties.

Layout (little-endian, every array naturally aligned):
  header  <8sIIIIff>  magic, n_states, n_edges, n_feat, n_cls, lo, step
  names   n_cls x 4 bytes, NUL-padded ISO codes
  start   u32[n_states+1]   CSR offsets into ev/eb
  fail    u32[n_states]
  out     i32[n_states]     feature index per state, -1 if none
  ev      u32[n_edges]      goto target, children sorted by byte
  pc      f32[n_cls]        class priors
  eb      u8[n_edges]       goto byte
  ptc     u8[n_feat][n_cls] score = lo + step * q
"""
import struct
import sys
from collections import deque

import numpy as np
from py3langid.langid import MODEL_DIR, MODEL_FILE
from py3langid.modelio import load_model

MAGIC = b'WLID0002'


def trie_from_dfa(delta):
  """Return (order, parent, pbyte, fail) for a dense AC automaton."""
  n_states = delta.shape[0]
  # BFS depth equals trie depth: reaching a node labelled s needs |s| bytes
  depth = np.full(n_states, -1, np.int64)
  depth[0] = 0
  queue, order = deque([0]), []
  while queue:
    u = queue.popleft()
    order.append(u)
    for v in np.unique(delta[u]):
      if depth[v] < 0:
        depth[v] = depth[u] + 1
        queue.append(v)
  if (depth < 0).any():
    raise ValueError('unreachable DFA states')

  # goto edges are exactly the transitions one level deeper
  us, bs = np.nonzero(depth[delta] == depth[:, None] + 1)
  vs = delta[us, bs]
  if len(vs) != n_states - 1 or len(np.unique(vs)) != n_states - 1:
    raise ValueError('DFA is not an Aho-Corasick trie')
  parent = np.zeros(n_states, np.int64)
  pbyte = np.zeros(n_states, np.int64)
  parent[vs], pbyte[vs] = us, bs

  fail = np.zeros(n_states, np.uint32)
  for v in order[1:]:
    u = parent[v]
    fail[v] = 0 if u == 0 else delta[fail[u], pbyte[v]]
  return order, parent, pbyte, fail


def main():
  if len(sys.argv) != 2:
    sys.exit(f'usage: {sys.argv[0]} OUTPUT.bin')
  out_path = sys.argv[1]

  ptc, pc, classes, nm, row, out = load_model(MODEL_DIR / MODEL_FILE)
  delta = np.frombuffer(nm, dtype=np.uint32).reshape(-1, 256)[
    np.frombuffer(row, dtype=np.uint16)]
  n_states = delta.shape[0]
  order, parent, pbyte, fail = trie_from_dfa(delta)

  kids = [[] for _ in range(n_states)]
  for v in order[1:]:
    kids[parent[v]].append((int(pbyte[v]), v))
  for k in kids:
    k.sort()

  # prove goto+fail reproduces every dense row before trusting it
  regen = np.zeros_like(delta)
  for s in order:
    r = np.zeros(256, np.uint32) if s == 0 else regen[fail[s]].copy()
    for b, v in kids[s]:
      r[b] = v
    regen[s] = r
  if not np.array_equal(regen, delta):
    raise ValueError('goto/fail does not reproduce the DFA')
  n_edges = n_states - 1
  print(f'DFA verified: {n_states} states, {n_edges} edges', file=sys.stderr)

  start = np.zeros(n_states + 1, np.uint32)
  start[1:] = np.cumsum([len(k) for k in kids])
  eb = np.fromiter((b for k in kids for b, _ in k), np.uint8, n_edges)
  ev = np.fromiter((v for k in kids for _, v in k), np.uint32, n_edges)

  ptc = np.asarray(ptc, np.float32)
  lo, hi = float(ptc.min()), float(ptc.max())
  step = (hi - lo) / 255
  qz = np.rint((ptc - lo) / step).astype(np.uint8)

  names = b''.join(c.encode().ljust(4, b'\0') for c in classes)
  if any(len(c) > 3 for c in classes):
    raise ValueError('language code longer than 3 bytes')
  with open(out_path, 'wb') as f:
    f.write(struct.pack('<8sIIIIff', MAGIC, n_states, n_edges,
                        ptc.shape[0], len(classes), lo, step))
    f.write(names)
    for a in (start, fail, np.asarray(out, np.int32), ev,
              np.asarray(pc, np.float32), eb, qz):
      f.write(np.ascontiguousarray(a).tobytes())
  print(f'wrote {out_path}: {len(classes)} languages, {ptc.shape[0]} features',
        file=sys.stderr)


if __name__ == '__main__':
  main()

#fin
