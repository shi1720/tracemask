"""A constrained JSON-over-SSE gateway; not a provider SDK or an EventSource client."""
import codecs
import json
from .core import StreamMask


class IncompleteStream(RuntimeError):
    pass


class SSEMaskGateway:
    """event: delta / data: {\"text\": ...}; event: done / data: {}.

    A socket close is not a successful application terminal. Decode UTF-8
    strictly, reject malformed JSON and unknown event types, discard pending
    on all errors. One instance per logical stream; no implicit reconnect.
    """
    def __init__(self, automaton, max_event_chars=1048576):
        self.masker = StreamMask(automaton)
        self.decoder = codecs.getincrementaldecoder('utf-8')('strict')
        self.line = []; self.data = []; self.kind = ''; self.cr = False
        self.first = True; self.done = False; self.failed = False
        self.size = 0; self.limit = max_event_chars

    def _line(self):
        line = ''.join(self.line); self.line.clear()
        if not line:
            if not self.data:
                self.kind = ''; self.size = 0
                return []
            value = json.loads('\n'.join(self.data))
            kind = self.kind or 'message'
            self.data.clear(); self.kind = ''; self.size = 0
            if kind == 'delta':
                if not isinstance(value, dict) or set(value) != {'text'} or not isinstance(value['text'], str):
                    raise ValueError('Invalid delta schema')
                return self.masker.push(value['text'])
            if kind == 'done' and value == {}:
                self.done = True
                return self.masker.finish()
            raise ValueError('Unknown or malformed application event')
        if line.startswith(':'):
            return []
        name, sep, value = line.partition(':')
        if value.startswith(' '):
            value = value[1:]
        if name == 'data':
            self.data.append(value)
        elif name == 'event':
            self.kind = value
        return []

    def feed(self, packet):
        if self.failed:
            raise RuntimeError('Gateway is closed')
        out = []
        try:
            text = self.decoder.decode(packet)
            for c in text:
                if self.first:
                    self.first = False
                    if c == '\ufeff':
                        continue
                if self.done:
                    if c not in '\r\n':
                        raise ValueError('Data after terminal event')
                    continue
                if c == '\n' and self.cr:
                    self.cr = False
                    continue
                self.cr = c == '\r'
                if c in '\r\n':
                    out.extend(self._line())
                else:
                    self.line.append(c); self.size += 1
                    if self.size > self.limit:
                        raise ValueError('Event exceeds configured size limit')
            return out
        except Exception:
            self.abort()
            raise

    def eof(self):
        if self.failed:
            raise RuntimeError('Gateway failed')
        try:
            self.decoder.decode(b'', final=True)
            if not self.done:
                raise IncompleteStream('No application done event')
        except Exception:
            self.abort()
            raise

    def abort(self):
        self.failed = True
        if not self.masker.closed:
            self.masker.abort()
        self.line.clear(); self.data.clear()


def encode_events(parts, done=True, newline='\n'):
    text = ''.join('event: delta'+newline+'data: '+json.dumps({'text': p}, ensure_ascii=False)+newline*2
                   for p in parts)
    if done:
        text += 'event: done'+newline+'data: {}'+newline*2
    return text.encode('utf-8')
