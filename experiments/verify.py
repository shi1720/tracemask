"""Verify saved trials independently. Imports no production implementation."""
import csv
import gzip
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[1]
docs = [json.loads(l) for l in (root/'data/corpus.jsonl').read_text().splitlines()]
oracles = {}
for d in docs:
    covered = set()
    # Separate regex-free occurrence search and explicit source-coordinate union.
    for p in d['patterns']:
        pos = d['text'].find(p)
        while pos >= 0:
            covered.update(range(pos, pos+len(p)))
            pos = d['text'].find(p, pos+1)
    oracles[d['id']] = covered
rows = {(int(r['id']),int(r['chunk']),r['method']):r
        for r in csv.DictReader((root/'results/trials.csv').open())}
seen = set()
with gzip.open(root/'results/traces.jsonl.gz', 'rt') as f:
    for l in f:
        t = json.loads(l); key = t['id'],t['chunk'],t['method']
        assert key not in seen
        seen.add(key); r = rows[key]; flags = set(t['masked']); oracle = oracles[t['id']]
        assert len(t['delay']) == int(r['n'])
        assert all(x>=0 for x in t['delay'])
        assert len(oracle-flags) == int(r['leaked'])
        assert len(flags-oracle) == int(r['overmasked'])
        assert int(flags==oracle) == int(r['exact'])
        assert math.isclose(sum(t['delay'])/len(t['delay']),float(r['mean_delay']),abs_tol=1e-10)
assert seen == set(rows)
print('PASS:', len(seen), 'saved traces; independent coverage, leakage, overmasking, delay arithmetic.')
