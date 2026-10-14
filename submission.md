# Code Europe AI 2027 session

Format: Stage Talk, Day 2 on-site. Designed for 40 minutes including questions; compatible with the live form's 40–55-minute label.
Primary 2027 track: AI Security, Safety & Governance. Live form label: Cybersecurity.
Speaker: Shivam Gupta. Contact: shivam1720406@gmail.com.

## Title

Redact Before Release: Literal Secrets in Streaming AI Gateways

## Public abstract

Learn how to build and test a streaming output filter that masks registered secrets before any part of a matched occurrence reaches a client, log, or speech service. We will implement the release boundary, measure its delay, and handle the byte splits and interrupted connections that a whole-response test misses.

The session follows TraceMask, an open-source reference gateway with an exact copy/mask contract. In 2,000 controlled streams drawn from 400 public instruction responses with artificial secrets, it matched an independent offline policy in every case and reduced mean added delay from 83.31 to 15.68 input code points versus safe fixed buffering. A simpler adaptive suffix buffer performed almost identically on this workload; we will examine the overlapping dictionaries where coverage-aware release actually helps, rather than claiming every application needs it.

Through a live SSE demonstration, we will split secrets across events, fragment UTF-8 bytes, drop a connection before completion, and compare actual released output. You will leave with a reproducible test harness, a dictionary-specific buffering bound, and concrete guidance for choosing a fixed buffer, adaptive holdback, or earliest-release implementation. The guarantee covers registered literal strings, not general PII detection or semantic moderation.

Code, paper, traces and reproduction commands: https://github.com/shi1720/tracemask

## Private committee pitch

Submission for Code Europe AI 2027, intended Track 05 (the live form still uses the Cybersecurity label). I am an applied AI engineer and founder of Siloed. My experience includes enterprise AI product engineering at Khoros/IgniteTech, building agent workflows, and creating verifiable coding-agent environments at micro1. This session is based on an implemented and measured research artifact, not a vendor demonstration or an untested production claim.

The artifact contains two proved release/buffering characterizations, a standard-library implementation, 12,000 saved six-method replay trials, independent trace verification, exhaustive continuation tests, 594 SSE byte-split cases, 128 local HTTP streams, and a pinned third-party integration probe. The paper explicitly reports the tiny primary gain over the simpler adaptive baseline and separates constructed stress cases from ordinary corpus results. I will explain what the data supports and where engineers should use the simpler design.

40-minute flow: 0–5, demonstrate a cross-event leak; 5–13, define exact masking and derive the release frontier; 13–21, implement matcher state and the dictionary-specific bound; 21–29, reproduce safe/unsafe buffering comparisons and the adaptive-baseline result; 29–35, live UTF-8 and disconnect fault injection; 35–40, deployment choices and questions. A recorded fixture replay provides an offline fallback for the demo. This is an original session proposal; no prior delivery of this talk is claimed.

Research manuscript and code: https://github.com/shi1720/tracemask
PDF: https://github.com/shi1720/tracemask/blob/main/paper/paper.pdf

## Speaker biography

Shivam Gupta is an applied AI engineer and founder of Siloed. He builds AI-enabled software and agent workflows, with experience in enterprise product engineering, evaluation infrastructure, and full-stack delivery. His work includes AI product engineering at Khoros/IgniteTech and verifiable coding-agent environments at micro1. He holds a B.Tech. in Computer Science and Design from IIIT Delhi. His current independent research focuses on testable contracts at the boundaries between AI systems and software infrastructure.

## Presenter notes

- Solo presenter. The user selected an on-site Stage Talk as the fallback because there are no confirmed co-panelists.
- No speaking recordings or co-presenters have been invented.
- The linked manuscript is supporting material. This CFP is not a paper-publication submission.

## Delivery status

Submitted on 14 October 2026 through the user-provided form. Confirmation: "Your response has been recorded." Decision pending. The live form retains its 2026 heading but explicitly accepts 2027 proposals; the pitch identifies the intended edition. See `submission_status.json`.
