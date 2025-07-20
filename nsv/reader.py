class Reader:
    def __init__(self, file_obj):
        self._file_obj = file_obj

    def __iter__(self):
        return self

    def __next__(self):
        acc = []
        for line in self._file_obj:
            if line == '\n':
                return acc
            if line[-1] == '\n':  # so as not to chop if missing newline at EOF
                line = line[:-1]
            acc.append(Reader.unescape(line))  # bruh
        # at the end of the file
        if acc:
            return acc
        else:  # an empty row would self-report in the cycle body
            raise StopIteration

    @staticmethod
    def unescape(s: str) -> str:
        if s == '\\':
            return ''
        if '\\' not in s:
            return s
        out = []
        escaped = False
        for c in s:
            if escaped:
                if c == 'n':
                    out.append('\n')
                elif c == '\\':
                    out.append('\\')
                else:
                    out.append('\\' + c)  # sus
                escaped = False
            else:
                if c == '\\':
                    escaped = True
                else:
                    out.append(c)
        return ''.join(out)

    @staticmethod
    def check(s: str):
        """Print warnings, if any."""
        line = 0
        col = 0
        escaped = False
        sus = []
        for pos, c in enumerate(s):
            if escaped:
                if c not in ('n', '\\'):
                    sus.append((pos, line, col))
                escaped = False
            elif c == '\\':
                escaped = True
            if c == '\n':
                line += 1
                col = 0
            else:
                col += 1
        if escaped:
            sus.append(len(s) - 1)
        for pos, line, col in sus:
            print(f'WARNING: Unescaped backslash at position {pos} ({line}:{col})')
        if s[-1] != '\n':
            print(f'WARNING: No newline at the end')
