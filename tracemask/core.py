from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    """A masked decision carries no raw character. Offset is a code-point index."""
    offset: int
    value: str | None

    @property
    def masked(self):
        return self.value is None


class Automaton:
    """Aho-Corasick trie, longest terminal and longest extendible suffix."""
    def __init__(self, patterns):
        self.patterns = tuple(sorted(set(patterns)))
        if any(not isinstance(p, str) or not p for p in self.patterns):
            raise ValueError('Patterns must be nonempty strings')
        self.next, self.fail, self.depth, self.match = [{}], [0], [0], [0]
        for p in self.patterns:
            q = 0
            for c in p:
                if c not in self.next[q]:
                    self.next[q][c] = len(self.next)
                    self.next.append({}); self.fail.append(0)
                    self.depth.append(self.depth[q] + 1); self.match.append(0)
                q = self.next[q][c]
            self.match[q] = len(p)
        self.proper = [0] * len(self.next)
        queue = deque(self.next[0].values())
        while queue:
            q = queue.popleft()
            f = self.fail[q]
            self.match[q] = max(self.match[q], self.match[f])
            self.proper[q] = self.depth[q] if self.next[q] else self.proper[f]
            for c, r in self.next[q].items():
                f = self.fail[q]
                while f and c not in self.next[f]:
                    f = self.fail[f]
                self.fail[r] = self.next[f].get(c, 0)
                queue.append(r)
        self.max_length = max(map(len, self.patterns), default=0)

    def advance(self, q, c):
        while q and c not in self.next[q]:
            q = self.fail[q]
        return self.next[q].get(c, 0)


class StreamMask:
    """A policy is immutable for the life of a stream; automata may be shared.

    modes: earliest, suffix (ablation), fixed (lag required), full.
    Only finish() means application-level successful termination. On a failed
    or cancelled transport call abort(), which irreversibly discards pending.
    """
    def __init__(self, automaton, mode='earliest', lag=0):
        if mode not in ('earliest', 'suffix', 'fixed', 'full') or lag < 0:
            raise ValueError('Invalid release mode or lag')
        self.a, self.mode, self.lag = automaton, mode, lag
        self.q = self.n = self.offset = self.peak = 0
        self.pending, self.coverage = deque(), deque()
        self.closed = False

    def _check(self):
        if self.closed:
            raise RuntimeError('Stream is closed')

    def _mark(self, start, end):
        start = max(start, self.offset)
        if start >= end:
            return
        while self.coverage and self.coverage[-1][1] >= start:
            start = min(start, self.coverage.pop()[0])
        self.coverage.append((start, end))

    def _covered(self):
        while self.coverage and self.coverage[0][1] <= self.offset:
            self.coverage.popleft()
        return bool(self.coverage and self.coverage[0][0] <= self.offset)

    def _drain(self, boundary, allow_masked):
        out = []
        while self.pending:
            masked = self._covered()
            if self.offset >= boundary and not (allow_masked and masked):
                break
            c = self.pending.popleft()
            out.append(Decision(self.offset, None if masked else c))
            self.offset += 1
        return out

    def push(self, text):
        self._check()
        out = []
        for c in text:
            self.pending.append(c); self.n += 1
            self.q = self.a.advance(self.q, c)
            m = self.a.match[self.q]
            if m:
                self._mark(self.n - m, self.n)
            if self.mode in ('earliest', 'suffix'):
                boundary = self.n - self.a.proper[self.q]
            elif self.mode == 'fixed':
                boundary = max(0, self.n - self.lag)
            else:
                boundary = 0
            out.extend(self._drain(boundary, self.mode == 'earliest'))
            self.peak = max(self.peak, len(self.pending))
        return out

    def finish(self):
        self._check()
        out = self._drain(self.n, False)
        self.closed = True
        self.coverage.clear()
        return out

    def abort(self):
        self._check()
        discarded = len(self.pending)
        self.pending.clear(); self.coverage.clear(); self.closed = True
        return discarded


def render(decisions, mask='*'):
    return ''.join(mask if d.masked else d.value for d in decisions)


def exact_pending_bound(automaton):
    """Exact dictionary-specific bound, by trie-prefix coverage enumeration.

    Optional analysis, not part of streaming hot path. O(S L) time with
    expected constant-time transitions. Coverage arrays are copied per edge.
    """
    bound = 0
    stack = [(0, [], 0)]
    while stack:
        q, coverage, acstate = stack.pop()
        if automaton.next[q]:
            first = next((i for i, flag in enumerate(coverage) if not flag), len(coverage))
            bound = max(bound, len(coverage)-first)
        for c, child in automaton.next[q].items():
            state = automaton.advance(acstate, c)
            flags = coverage + [False]
            m = automaton.match[state]
            if m:
                flags[-m:] = [True]*m
            stack.append((child, flags, state))
    return bound
