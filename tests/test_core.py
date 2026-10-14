import itertools
import json
import random
import unittest
from pathlib import Path
from tracemask import Automaton, StreamMask
from tracemask.core import exact_pending_bound
from tests.oracle import mask_flags, frontier


def words(alphabet, maxlen):
    return [''.join(x) for n in range(maxlen+1)
            for x in itertools.product(alphabet, repeat=n)]


class CoreTests(unittest.TestCase):
    def test_exhaustive_outputs(self):
        ps = words('ab', 2)[1:]
        count = 0
        for bits in range(1, 1 << len(ps)):
            pats = [p for j, p in enumerate(ps) if bits >> j & 1]
            a = Automaton(pats)
            for text in words('ab', 8):
                s = StreamMask(a)
                out = []
                for c in text:
                    out.extend(s.push(c))
                out.extend(s.finish())
                self.assertEqual([d.masked for d in out], mask_flags(text, pats))
                self.assertLessEqual(s.peak, a.max_length - 1)
                count += 1
        print('exhaustive output cases:', count)

    def test_exact_frontier_by_continuations(self):
        ps = words('ab', 3)[1:]
        dicts = [(p,) for p in ps] + list(itertools.combinations(ps, 2))
        count = 0
        for pats in dicts:
            a = Automaton(pats)
            for text in words('ab', 6):
                s = StreamMask(a)
                emitted = s.push(text)
                candidates = [mask_flags(text + tail, pats)[:len(text)]
                              for tail in words('ab', a.max_length - 1)]
                expected = next((i for i in range(len(text))
                                 if len({c[i] for c in candidates}) > 1), len(text))
                self.assertEqual(len(emitted), expected, (pats, text))
                self.assertEqual(frontier(text, pats), expected)
                count += 1
        print('continuation frontier cases:', count)

    def test_partitions_unicode_random(self):
        rng = random.Random(91)
        for _ in range(2000):
            pats = [''.join(rng.choices('abé🙂中', k=rng.randrange(1, 12)))
                    for _ in range(rng.randrange(1, 15))]
            text = ''.join(rng.choices('abé🙂中', k=80)) + pats[0] + pats[-1]
            s = StreamMask(Automaton(pats)); out = []; i = 0
            while i < len(text):
                j = i + rng.randrange(1, 20)
                out.extend(s.push(text[i:j])); i = j
            out.extend(s.finish())
            self.assertEqual([d.masked for d in out], mask_flags(text, pats))

    def test_all_partitions(self):
        count = 0
        for text in words('ab', 7)[1:]:
            a = Automaton(['aba', 'bab', 'ab', 'bba'])
            for bits in range(1 << (len(text)-1)):
                cuts = [0] + [i+1 for i in range(len(text)-1) if bits >> i & 1] + [len(text)]
                s = StreamMask(a); out = []
                for x, y in zip(cuts, cuts[1:]):
                    out.extend(s.push(text[x:y]))
                out.extend(s.finish())
                self.assertEqual([d.masked for d in out], mask_flags(text, a.patterns))
                count += 1
        print('all partition cases:', count)

    def test_lifecycle_and_overlap(self):
        s = StreamMask(Automaton(['ab', 'abcd']))
        self.assertEqual([d.masked for d in s.push('ab')], [True, True])
        self.assertEqual(s.push('c'), [])
        self.assertEqual(s.abort(), 1)
        for fn in (lambda: s.push('d'), s.finish, s.abort):
            self.assertRaises(RuntimeError, fn)
        s = StreamMask(Automaton([]))
        self.assertEqual(len(s.push('text')), 4)
        self.assertEqual(s.finish(), [])
        self.assertRaises(ValueError, Automaton, [''])

    def test_dictionary_specific_bound(self):
        ps = words('ab', 3)[1:]
        dicts = [(p,) for p in ps] + list(itertools.combinations(ps, 2))
        for pats in dicts:
            a = Automaton(pats)
            bound = exact_pending_bound(a)
            observed = 0
            for text in words('ab', 7):
                s = StreamMask(a); s.push(text)
                observed = max(observed, s.peak)
            self.assertEqual(observed, bound, pats)
        self.assertEqual(exact_pending_bound(Automaton(['a','a'*255+'b'])), 0)
        self.assertEqual(exact_pending_bound(Automaton(['a'*256])), 255)
        print('dictionary-specific bound cases:', len(dicts)+2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
