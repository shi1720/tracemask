"""Offline conference demo: python -m experiments.demo (from the repo root)."""
from tracemask import Automaton
from tracemask.core import render, exact_pending_bound
from tracemask.sse import SSEMaskGateway, IncompleteStream, encode_events

policy = Automaton(['tenant-secret-123'])
print('Exact maximum pending code points:', exact_pending_bound(policy))
for success in (True, False):
    parts = ['Public: é🙂 ', 'tenant-', 'secret-', '123', ' done'] if success else ['Public: é🙂 ', 'tenant-secr']
    wire = encode_events(parts, done=success)
    gateway = SSEMaskGateway(policy)
    output = []
    for i in range(0, len(wire), 1):
        output.extend(gateway.feed(wire[i:i+1]))
    try:
        gateway.eof()
        status = 'application success'
    except IncompleteStream:
        status = 'aborted; unresolved tail discarded'
    print(status+':', render(output))
