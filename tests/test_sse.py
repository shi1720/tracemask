import http.client
import json
import random
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tracemask import Automaton
from tracemask.core import render
from tracemask.sse import SSEMaskGateway, IncompleteStream, encode_events
from tests.oracle import mask_flags


class SSETests(unittest.TestCase):
    def test_every_byte_split(self):
        parts = ['Hello é🙂 ', 'secret-', 'value', ' / 中 end']
        patterns = ['secret-value', 'é🙂']
        text = ''.join(parts)
        expected = mask_flags(text, patterns)
        total = 0
        for newline in ['\n', '\r\n', '\r']:
            wire = b'\xef\xbb\xbf' + encode_events(parts, newline=newline)
            for k in range(len(wire)+1):
                g = SSEMaskGateway(Automaton(patterns)); out = []
                # Feeding only nonempty packets avoids a call after terminal.
                for p in [wire[:k], wire[k:]]:
                    if p:
                        out.extend(g.feed(p))
                g.eof()
                self.assertEqual([d.masked for d in out], expected)
                total += 1
        print('SSE every-byte partition cases:', total)

    def test_incomplete_and_invalid(self):
        g = SSEMaskGateway(Automaton(['secret']))
        self.assertEqual(g.feed(encode_events(['secr'], done=False)), [])
        self.assertRaises(IncompleteStream, g.eof)
        self.assertEqual(len(g.masker.pending), 0)
        for packet in [b'event: delta\ndata: not-json\n\n', b'\xff',
                       b'event: delta\ndata: {"text": 1}\n\n',
                       b'event: other\ndata: {}\n\n']:
            g = SSEMaskGateway(Automaton(['secret']))
            self.assertRaises((ValueError, UnicodeError), g.feed, packet)
            self.assertTrue(g.failed)
        g = SSEMaskGateway(Automaton([]), max_event_chars=10)
        self.assertRaises(ValueError, g.feed, b'data: '+b'x'*20)

    def test_real_http_streams(self):
        # No model service: a local fixture, deliberately splitting UTF-8 bytes.
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                fail = self.path == '/abort'
                parts = ['Public: é🙂 ', 'tenant-', 'secret-', '123', ' done']
                if fail:
                    parts = ['Public: é🙂 ', 'tenant-secr']
                wire = encode_events(parts, done=not fail)
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Content-Length', str(len(wire)))
                self.end_headers()
                for i in range(0, len(wire), 3):
                    self.wfile.write(wire[i:i+3]); self.wfile.flush()
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        t = threading.Thread(target=server.serve_forever, daemon=True); t.start()
        try:
            for k in range(1, 65):
                for fail in [False, True]:
                    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                    conn.request('GET', '/abort' if fail else '/')
                    response = conn.getresponse()
                    g = SSEMaskGateway(Automaton(['tenant-secret-123'])); out = []
                    while packet := response.read(k):
                        out.extend(g.feed(packet))
                    if fail:
                        self.assertRaises(IncompleteStream, g.eof)
                        self.assertEqual(render(out), 'Public: é🙂 ')
                    else:
                        g.eof()
                        self.assertEqual(render(out), 'Public: é🙂 '+ '*'*17 + ' done')
                    conn.close()
        finally:
            server.shutdown(); server.server_close(); t.join()
        print('local HTTP integration streams:', 128)


if __name__ == '__main__':
    unittest.main(verbosity=2)
