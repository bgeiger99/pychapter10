
try:
    import cbitstruct as bitstruct
except ImportError:
    import bitstruct


class BitFormat:
    """Bitstruct wrapper that allows for compiling from readable format
    strings.
    """

    def __init__(self, src, byteswap=None):
        self.byteswap = byteswap
        fmt_str = ''
        names = []
        for line in src.strip().splitlines():
            line = line.strip().split()
            if not line:
                continue
            if len(line) == 1 or line[-1].lower().endswith('reserved'):
                fmt = line[0]
            else:
                fmt, name = line
                names.append(name)
            fmt_str += fmt

        # Default to little endian if we're not explicitly defining swapping
        if not byteswap and fmt_str[-1] not in '<>':
            fmt_str += '<'

        self._compiled = bitstruct.compile(fmt_str, names=names)

    def __getattr__(self, name, default=None):
        if name in ('byteswap', 'unpack', 'raw'):
            return object.__getattr__(self, name, default)
        return getattr(self._compiled, name, default)

    def unpack(self, data):
        if self.byteswap:
            data = bitstruct.byteswap(self.byteswap, data)
        self.raw = data
        return self._compiled.unpack(data)


def compile_fmt(src, byteswap=None):
    """Compile helper that takes a readable string and creates a bitstruct
    CompiledFormatDict.
    """

    return BitFormat(src, byteswap)


class Buffer(object):
    """File wrapper that raises EOF on a short read."""

    def __init__(self, io):
        self.io = io
        self.tell = self.io.tell
        self.seek = self.io.seek

    def read(self, size=None):
        value = self.io.read(size)
        if size and len(value) != size:
            raise EOFError
        return value
