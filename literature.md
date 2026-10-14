# Literature and overlap audit

Audit date: 14 October 2026. This is a bounded desk review, not a guarantee that no overlapping unpublished or unindexed result exists.

## Question selection

The local research folder was inventoried and every available PDF was text-extracted into private task scratch space. Abstracts and relevant introductions were checked before selection. Existing work includes tool-cache coupling, prefix-cache retention, agent compensation, numeric wire fidelity, retrieval fusion, personal memory, counterfactual winner logs, and robot interruption timing. None of the inspected manuscripts studies the exact copy/mask release frontier or the dictionary-specific pending bound for overlapping literal secrets. The general interest in agent-system interfaces is shared; the mathematical object, implementation, data, and results here are separate. Existing personal details and unpublished manuscript text are not included in the public artifact.

Three candidate directions were checked: speculative agent transactions; schema compatibility; streaming literal redaction. Transactions overlap agent compensation and existing optimistic concurrency. Schema fidelity is too close to the author's numeric transport manuscript. The selected problem offers deterministic oracles, real byte/event interfaces, and an engineering result that can be tested on available hardware.

## Search families

Web searches combined: LLM streaming redaction / secret masking / holdback / chunk boundaries; online redaction / minimum or optimal latency; literal masking / Aho-Corasick / overlap; subsequential transducers / longest common output prefix; streaming guardrails / release-boundary equivalence. Primary papers, author PDFs, pinned source code, dataset documentation, and standards were used in the manuscript. Product claims were treated as documentation, not independent performance evidence.

## Closest prior work

| Source | Established contribution | Consequence for this paper |
|---|---|---|
| Aho & Corasick, CACM 1975, DOI 10.1145/360825.360855 | Persistent finite-dictionary matching | No claim to invent the matcher or linear matching |
| Mohri, Computational Linguistics 1997, https://aclanthology.org/J97-2003/ | Finite-state transduction and determined output prefixes | No claim to invent common-output-prefix advancement |
| Schneider, TISSEC 2000, DOI 10.1145/353323.353382 | Runtime monitoring of enforceable policies | No claim to invent runtime suppression |
| Ligatti, Bauer & Walker, IJIS 2005, https://users.ece.cmu.edu/~lbauer/papers/2005/ijis2005-editauto.pdf | Edit automata | Output transformation is established |
| Frost, arXiv:2608.10279v2 | Exact first-withheld-chunk equivalence for conjunction policies | Different policy: stop monitor versus exact per-coordinate redaction |
| SentGuard, arXiv:2606.02041; StreamGuard, arXiv:2604.03962 | Statistical semantic streaming moderation | Complementary scope; do not imply general safety here |
| Rust aho-corasick DESIGN.md | Match selection, overlap and streaming tradeoffs | Must specify union-of-all-occurrences, not assume replacement semantics |
| Sether 0.7.1, commit 14ee74e2afca52c57f01ab43ee969db9d2429d0c | Streaming redaction, vaults, middleware, bounded candidate guards | Existing practical solution, controlled custom-detector probe only |
| Netresearch ADR-088 (18 July 2026) | Live redaction with fixed holdback | Fixed buffering is prior art |
| TinyVault Codemap documentation | Literal output masking with explicit residuals | Commercial use case exists; semantic leakage remains outside literal guarantees |
| WHATWG HTML §9.2 | SSE framing and UTF-8 semantics | Decode and frame before matching; completion is application-specific |

## Defensible contribution

A specialized closed form for the earliest exact **tagged source-coordinate** masking decisions, an exact dictionary-specific pending bound attained on a proper dictionary prefix, a coverage-interval implementation, and a reproducible test artifact. The primary empirical advantage over a simple adaptive suffix baseline is negligible and is prominently reported. A constructed overlap separation is not a production prevalence result. Do not describe this as an unprecedented general guardrail, industry-defining breakthrough, guaranteed publishable result, or patent clearance.

## Practical landscape

Sether supplies reversible placeholders and middleware, Netresearch integrates live redaction into an application framework, and TinyVault exposes literal redaction at a secrets/tool boundary. The potential product direction is a testable tenant-scoped release layer inside such infrastructure, with versioned dictionary policies and trace diagnostics. This desk review does not establish total addressable market, willingness to pay, a unique startup opportunity, or freedom to operate.

## Venue fit

The official Code Europe AI 2027 CFP at https://www.codeeurope.pl/cfp accepts engineering sessions, not archival research papers. Its stated criteria favor specific systems, measured results, technical depth, and audience fit. Intended 2027 track: AI Security, Safety & Governance. The user-provided live Google Form still labels the track Cybersecurity and carries a 2026 heading, but explicitly says it is collecting 2027 proposals. The committee pitch explicitly identifies the 2027 edition. The form's on-site Stage Talk is the authorized solo-presenter fallback after the panel requirement was discussed.
