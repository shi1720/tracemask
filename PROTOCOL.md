# Frozen evaluation protocol
Written 14 October 2026, before the evaluation scripts were run.

Question: for a fixed finite dictionary of nonempty literal strings, can a streaming gateway reproduce the union-of-all-occurrences offline masking policy while releasing every irrevocably determined source-coordinate decision at each input prefix?

Primary comparisons: TraceMask; fixed L-1 lag with persistent match coverage (safe); fixed 32 lag with persistent coverage (potentially unsafe); chunk-local masking; full buffering; prefix-only holdback (safe, omits known-coverage optimization). All use identical dictionaries and the same independent offline span oracle. Engineered baselines are not vendor products.

Data: sample 400 Dolly-15k responses of 200--3000 Unicode code points, deterministic sample seed 1720406. Each response is paired with one artificial secret of cyclic lengths 16,32,64,128,256. Half the secrets are random ASCII alphanumerics, half sampled response substrings. Insert the selected secret at the response midpoint, delimited by spaces; also register three distractors. Do not interpret this as spontaneous leakage by a model. Replay each at chunk sizes 1,4,16,64 and seeded random sizes 1--64. Token timing is not measured.

Primary metrics: leaked source positions, overmasked positions, exact final agreement, mean added delay in input code points per source position, peak pending code points. Pairing and uncertainty: average over chunk schedules within each document, then paired bootstrap 10,000 resamples of documents, seed 2027, report percentile 95% intervals for mean delay differences. Intervals quantify corpus sampling variability, not failure probabilities.

Mechanism tests: exhaustive binary texts length <=8 and every nonempty subset of binary patterns length <=2; exact frontier tested against enumerated continuations length <=L-1 including termination, under dictionaries length <=3. Random overlapping dictionaries, Unicode, arbitrary chunking. Abort discards pending, successful application terminal flushes; reuse after either state fails.

Integration: local HTTP/SSE fixture with JSON content events, explicit done event, fragmented UTF-8 byte reads, multiple streams and early disconnects. Do not call a transport EOF successful completion. Pin public sources and data hashes. Separately time dictionary construction and processing on the local machine; report implementation times as local measurements, not deployment SLAs.

Analysis amendments must be documented; failures may not be removed. All primary trials retained. No tuning of parameters from the evaluation outcomes.
