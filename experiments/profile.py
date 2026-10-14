import json
import platform
import random
import statistics
import sys
import time
from pathlib import Path
from tracemask import Automaton, StreamMask

root = Path(__file__).resolve().parents[1]
rng = random.Random(2028)
text = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz ', k=65536))
rows = []
for count in [4, 64, 512, 4096]:
    pats = [''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=24)) for _ in range(count)]
    builds = []; timings = []
    for repeat in range(8):
        t = time.perf_counter_ns(); a = Automaton(pats)
        compile_ms = (time.perf_counter_ns()-t)/1e6
        s = StreamMask(a)
        t = time.perf_counter_ns()
        for i in range(0,len(text),16):
            s.push(text[i:i+16])
        s.finish()
        process_ms = (time.perf_counter_ns()-t)/1e6
        if repeat:  # one explicit warm-up; seven recorded measurements
            builds.append(compile_ms); timings.append(process_ms)
    rows.append(dict(patterns=count,states=len(a.next),codepoints=len(text),chunk=16,
                     compile_ms=builds,process_ms=timings,peak_pending=s.peak))
stress = []
for mode in ['earliest','suffix','fixed']:
    s = StreamMask(Automaton(['a', 'a'*255+'b']), mode=mode, lag=255)
    total_delay = 0; emitted = 0
    for i in range(65536):
        out = s.push('a'); emitted += len(out)
        total_delay += sum(i-d.offset for d in out)
        assert all(d.masked for d in out)
    out = s.finish(); emitted += len(out)
    total_delay += sum(65535-d.offset for d in out)
    assert all(d.masked for d in out) and emitted == 65536
    stress.append(dict(mode=mode,n=65536,mean_delay=total_delay/65536,peak_pending=s.peak))
result = dict(environment=dict(python=sys.version,platform=platform.platform()),
              timing=rows,overlap_stress=stress)
(root/'results/profile.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
