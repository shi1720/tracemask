"""Independent brute-force specification. No production matcher imports."""


def mask_flags(text, patterns):
    flags = [False] * len(text)
    for i in range(len(text)):
        for p in patterns:
            if text.startswith(p, i):
                for j in range(i, i + len(p)):
                    flags[j] = True
    return flags


def frontier(text, patterns):
    flags = mask_flags(text, patterns)
    ambiguous = set()
    for i in range(len(text)):
        tail = text[i:]
        if any(len(tail) < len(p) and p.startswith(tail) for p in patterns):
            ambiguous.update(range(i, len(text)))
    return next((i for i, masked in enumerate(flags)
                 if not masked and i in ambiguous), len(text))
