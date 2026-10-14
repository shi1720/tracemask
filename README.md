# TraceMask

Earliest-release literal redaction for streaming AI gateways. Research and reference implementation by **Shivam Gupta**.

[Read the paper](paper/paper.pdf) · [Frozen protocol](PROTOCOL.md) · [Results](results/summary.json) · [Conference session](submission.md)

TraceMask masks every source coordinate covered by any occurrence of a registered literal and copies all others. It releases decisions as soon as every continuation agrees. It also computes the exact maximum pending text for a dictionary. It is a reference implementation for known literal secrets, not a general PII detector.

## Measured results

On 400 public instruction responses with artificial secret insertion and five chunk schedules:

| Method | Exact streams / 2,000 | Mean added filter delay, input code points |
|---|---:|---:|
| TraceMask | 2,000 | 15.68 |
| Adaptive suffix holdback | 2,000 | 15.68 |
| Safe fixed L-1 | 2,000 | 83.31 |
| Full response | 2,000 | 336.48 |

The reduction versus safe fixed buffering is 67.64 code points, paired document-bootstrap 95% interval [62.42, 72.76]. The incremental benefit over adaptive suffix holdback is only 0.000751 code points on this corpus. A constructed overlapping dictionary separates them sharply. These are controlled replay results, not measured rates of model leakage or production latency.

## Quick start

Python >=3.10 for the core; Python >=3.11 for the pinned analysis dependencies. The core has no third-party dependencies.

```python
from tracemask import Automaton, StreamMask
from tracemask.core import render, exact_pending_bound

policy = Automaton(['ab', 'abcd'])
stream = StreamMask(policy)
print(render(stream.push('ab')))  # **: final masks, even if abcd remains possible
print(render(stream.push('c')))   # nothing: c is unresolved
print(render(stream.push('d')))   # **
print(render(stream.finish()))    # successful APPLICATION termination only
print(exact_pending_bound(policy))
```

Call `abort()` on cancellation, transport failure, or malformed input. Do not unconditionally call `finish()` in a cleanup block. Each logical stream needs its own state. A compiled, unmodified automaton can be shared. Positions and length bounds use Unicode code points, not UTF-8 bytes or model tokens. Normalization and escaping are explicit application responsibilities.

`tracemask.sse.SSEMaskGateway` demonstrates a strict JSON-over-SSE application protocol (`delta` with `{"text": "..."}`, `done` with `{}`). It is a bounded fixture adapter, not a full provider SDK or reconnecting EventSource implementation. The application must place it before every sink that needs redacted output.

## Reproduce and verify

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -v
python experiments/verify.py
PYTHONPATH=. python experiments/run.py
PYTHONPATH=. python experiments/profile.py
PYTHONPATH=. python experiments/figures.py
tectonic --outdir paper paper/paper.tex
```

The first two commands after installation verify the core and recorded primary traces. `run.py` reproduces the deterministic primary experiment from the supplied corpus. Timings from `profile.py` depend on the machine. Figures use Matplotlib. The original evaluation used Python 3.12.14 / NumPy 2.3.5; original figures used Python 3.9 / NumPy 1.26.4 / Matplotlib 3.9.4. Requirements provide a single supported Python >=3.11 analysis environment; rendered fonts may differ slightly. The original figure files are included.

To rebuild the derived corpus, download the source JSONL linked in `data/manifest.json`, verify its SHA-256, then run:

```sh
PYTHONPATH=. python experiments/run.py /path/to/databricks-dolly-15k.jsonl
```

The derived corpus is a deterministic 400-record sample with inserted **fictional** secrets. Databricks Dolly-15k supplies public instruction responses, not model outputs in this evaluation. See `data/LICENSE.md` for attribution and modifications.

For the supplementary third-party probe, use Node.js >=18 and npm:

```sh
git clone https://github.com/raeven-co/sether.git /tmp/sether-tracemask
cd /tmp/sether-tracemask
git checkout 14ee74e2afca52c57f01ab43ee969db9d2429d0c
npm ci --ignore-scripts
npm run build
cd /path/to/tracemask
node experiments/sether_probe.mjs /tmp/sether-tracemask/dist/index.js
```

This executes Sether's custom literal-detector interface without modifying its source. It separates selected holdback-bound failures from a byte-decoding failure; it does not evaluate built-in detector quality. Exact pin and raw outcomes are in `results/sether_probe.json`.

## Artifact map

- `tracemask/`: Aho-Corasick core, tagged decisions, bound analyzer, constrained SSE gateway.
- `tests/`: independently expressed specification, exhaustive continuation tests, random Unicode cases, real local HTTP fixtures.
- `experiments/`: corpus preparation, six-method replay, independent verifier, profile, figures, pinned third-party probe.
- `data/`: frozen derived corpus, attribution, source manifest.
- `results/`: all 12,000 trial rows, compressed coordinate/delay traces, summaries, raw timing samples, conformance logs.
- `paper/`: complete LaTeX source, figures and final PDF.
- `PROTOCOL.md`, `AMENDMENTS.md`: frozen primary design and explicitly separated supplementary work.
- `literature.md`: dated search and overlap assessment.

## Exact guarantee and limits

The mathematical guarantee assumes an immutable finite dictionary and exact decoded-string matching. It applies to the union of **all** occurrence spans, including overlaps, and requires no overmasking on successful finite input. Tagged mask records contain no underlying source character. The printable `*` renderer leaks masked lengths and positions. Unknown secrets, transformed strings, semantic leakage, timing side channels, unguarded sinks, and policy mutation are outside the contract. A valid terminal releases unmatched partial prefixes; an abnormal termination discards unresolved text. A bound in code points is not a wall-clock bound on a stalled upstream stream.

The main gain in the primary experiment comes from adaptive suffix matching. Prefer the simpler adaptive baseline when its tiny measured delay difference is acceptable. This repository does not assert broad safety or benchmark superiority over native implementations.

## License and citation

Original code: MIT, copyright 2026 Shivam Gupta. Derived Dolly text: CC BY-SA 3.0, Databricks. The manuscript is an author research manuscript, not an accepted or peer-reviewed publication. A conference talk submission is separate from publication status.

```bibtex
@misc{gupta2026tracemask,
  author = {Gupta, Shivam},
  title = {TraceMask: Earliest-Release Guarantees for Literal Redaction in Streaming AI Gateways},
  year = {2026},
  howpublished = {Research manuscript and reproducible artifact},
  url = {https://github.com/shi1720/tracemask}
}
```
