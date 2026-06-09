class Reader:
    def __init__(self, file_obj):
        self._file_obj = file_obj
        self._line_buffer = ''  # incomplete line at EOF, preserved for next call
        self._row_buffer = []  # incomplete row at EOF, preserved for next call

    def __iter__(self):
        return self

    def __next__(self):
        for line in self._file_obj:
            line = self._line_buffer + line
            self._line_buffer = ''
            if line == '\n':
                row, self._row_buffer = self._row_buffer, []
                return row
            if line[-1] == '\n':
                self._row_buffer.append(Reader.unescape(line[:-1]))
            else:  # no trailing newline only happens at EOF: incomplete line, keep
                self._line_buffer = line
        # at the end of the file; incomplete row stays buffered for resumption
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
            sus.append((len(s) - 1, line, col))
        for pos, line, col in sus:
            print(f'WARNING: Unescaped backslash at position {pos} ({line}:{col})')
        if s[-1] != '\n':
            print(f'WARNING: No newline at the end')
