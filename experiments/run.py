"""Seeded corpus replay. Run from repository root, with Python >=3.10."""
import csv
import gzip
import hashlib
import json
import platform
import random
import sys
import time
from pathlib import Path
import numpy as np
from tracemask import Automaton, StreamMask
from tests.oracle import mask_flags

ROOT = Path(__file__).resolve().parents[1]


def prepare(source):
    records = [json.loads(line) for line in Path(source).read_text().splitlines()]
    eligible = [(i, r['response']) for i, r in enumerate(records)
                if 200 <= len(r['response']) <= 3000]
    rng = random.Random(1720406)
    chosen = rng.sample(eligible, 400)
    docs = []
    for k, (idx, response) in enumerate(chosen):
        length = [16, 32, 64, 128, 256][k % 5]
        if k % 2:
            # Responses shorter than a selected phrase use a repeated response.
            base = response if len(response) >= length else response * 2
            start = rng.randrange(len(base)-length+1)
            secret = base[start:start+length]
            kind = 'phrase'
        else:
            secret = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))
            kind = 'identifier'
        pats = [secret] + [''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))
                           for _ in range(3)]
        text = response[:len(response)//2] + ' ' + secret + ' ' + response[len(response)//2:]
        docs.append(dict(id=k, source_row=idx, text=text, patterns=pats,
                         kind=kind, length=length))
    (ROOT/'data/corpus.jsonl').write_text(''.join(json.dumps(d, ensure_ascii=False)+'\n' for d in docs))
    manifest = dict(source='https://huggingface.co/datasets/databricks/databricks-dolly-15k',
                    source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),
                    source_records=len(records), eligible_records=len(eligible),
                    derived_records=len(docs), seed=1720406,
                    license='CC-BY-SA-3.0', modification='Artificial secrets inserted; four literals per response.')
    (ROOT/'data/manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


def chunks(text, size, seed):
    rng = random.Random(seed); i = 0
    while i < len(text):
        k = size if size else rng.randint(1, 64)
        yield text[i:i+k]; i += k


def evaluate():
    docs = [json.loads(l) for l in (ROOT/'data/corpus.jsonl').read_text().splitlines()]
    rows = []
    tracefile = gzip.open(ROOT/'results/traces.jsonl.gz', 'wt', encoding='utf-8')
    modes = ['earliest', 'suffix', 'fixed_safe', 'fixed32', 'chunk', 'full']
    started = time.perf_counter()
    for doc in docs:
        text, pats = doc['text'], doc['patterns']
        expected = np.array(mask_flags(text, pats), dtype=bool)
        a = Automaton(pats)
        for size in [1, 4, 16, 64, 0]:
            parts = list(chunks(text, size, 9000 + doc['id']))
            arrival = np.concatenate([np.full(len(p), t) for p, t in zip(parts, np.cumsum(list(map(len, parts))))])
            for mode in modes:
                if mode != 'chunk':
                    s = StreamMask(a, mode='fixed' if mode.startswith('fixed') else mode,
                                   lag=a.max_length-1 if mode == 'fixed_safe' else 32)
                flags = []; delays = []; seen = 0
                for part in parts:
                    seen += len(part)
                    if mode == 'chunk':
                        f = mask_flags(part, pats); flags.extend(f); delays.extend([0]*len(part))
                    else:
                        out = s.push(part)
                        flags.extend(d.masked for d in out)
                        delays.extend(seen - arrival[d.offset] for d in out)
                if mode != 'chunk':
                    out = s.finish(); flags.extend(d.masked for d in out)
                    delays.extend(len(text)-arrival[d.offset] for d in out)
                flags = np.array(flags, dtype=bool)
                tracefile.write(json.dumps(dict(id=doc['id'], chunk=size, method=mode,
                    masked=np.flatnonzero(flags).tolist(),
                    delay=list(map(int, delays))))+'\n')
                rows.append(dict(id=doc['id'], kind=doc['kind'], length=doc['length'],
                                 chunk=size, method=mode, n=len(text), sensitive=int(expected.sum()),
                                 leaked=int((expected & ~flags).sum()),
                                 overmasked=int((~expected & flags).sum()), exact=int(np.array_equal(expected, flags)),
                                 mean_delay=float(np.mean(delays)), p95_delay=float(np.percentile(delays,95)),
                                 peak_pending=0 if mode == 'chunk' else s.peak))
        if doc['id'] % 100 == 0:
            print('document', doc['id'], 'elapsed', round(time.perf_counter()-started, 1), flush=True)
    tracefile.close()
    with (ROOT/'results/trials.csv').open('w') as f:
        w = csv.DictWriter(f, rows[0]); w.writeheader(); w.writerows(rows)
    summary = {}
    for mode in modes:
        rr = [r for r in rows if r['method'] == mode]
        summary[mode] = dict(trials=len(rr), exact=sum(r['exact'] for r in rr),
                             leaking_trials=sum(r['leaked'] > 0 for r in rr),
                             leaked_positions=sum(r['leaked'] for r in rr),
                             overmasked_positions=sum(r['overmasked'] for r in rr),
                             mean_delay=float(np.mean([r['mean_delay'] for r in rr])),
                             max_pending=max(r['peak_pending'] for r in rr))
    rng = np.random.default_rng(2027)
    # Document-level pairing, each of the five schedules weighted equally.
    bydoc = {m: np.array([np.mean([r['mean_delay'] for r in rows if r['method']==m and r['id']==d['id']])
                          for d in docs]) for m in modes}
    resamples = rng.integers(0, len(docs), (10000, len(docs)))
    contrasts = {}
    for mode in ['fixed_safe', 'suffix', 'full']:
        delta = bydoc[mode] - bydoc['earliest']
        boots = delta[resamples].mean(axis=1)
        contrasts[mode+'-earliest'] = dict(mean=float(delta.mean()),
                    ci95=list(map(float, np.quantile(boots,[.025,.975]))))
    result = dict(methods=summary, contrasts=contrasts, documents=len(docs),
                  total_trials=len(rows), seconds=time.perf_counter()-started,
                  machine=dict(python=sys.version, platform=platform.platform(), processor=platform.processor()))
    (ROOT/'results/summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if len(sys.argv)>1:
        prepare(sys.argv[1])
    evaluate()
