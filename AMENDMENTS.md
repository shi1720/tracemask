# Protocol clarifications and supplementary work

The frozen PROTOCOL.md is unchanged (SHA-256 2ec70a06cc1ac894152b8dcbb53663b73b62743fff7e31bbae4147a7db5c1789).

- Primary delay is release-chunk endpoint minus arrival-chunk endpoint for each source position, measured in input code points. This removes transport chunk batching from added filter delay.
- The seeded corpus includes 15,011 source records, of which 7,119 meet the response-length filter. For a requested 256-character phrase from a shorter response, the response is repeated twice before selecting the phrase; this occurs only in artificial secret construction. This implementation choice is recorded in the corpus generator and is not a data exclusion.
- Complete trace recording and an independent verifier were added after the first primary run. The deterministic primary experiment was rerun with the same inputs and parameters. No primary result changed.
- Supplementary tests developed after primary results: exact dictionary-specific pending bound, a constructed overlap workload, a local CPU scaling profile, and a controlled probe of Sether 0.7.1 at a pinned commit. These are mechanism and integration diagnostics, not preregistered prevalence estimates.
- A development SSE test exposed completion on CR before a separately delivered LF. The parser was corrected to accept only trailing newline characters after the terminal event. All 594 two-packet split cases then passed. Earlier failure logs are retained in work history; final verified logs are in results/.
- The system Python was 3.9, which cannot interpret the union annotation used here. All reported successful runs use the bundled Python 3.12.14. The project requires Python >=3.10.
