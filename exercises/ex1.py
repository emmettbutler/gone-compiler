import re

PATTERNS = [
    ('NUMBER', r'(?P<NUMBER>\d+)'),
    ('ID', r'(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)'),
    ('WS', r'(?P<WS>\s+)'),
    ('EQ', r'(?P<EQ>)=='),
    ('ASSIGN', r'(?P<ASSIGN>=)'),
]
KEYWORDS = {'for': 'FOR', 'if': 'IF', 'while': 'WHILE'}
master = "|".join([a[1] for a in PATTERNS])


def tokenizer(pat, text):
    index = 0
    while index < len(text):
        m = pat.match(text, index)
        if m:
            yield m
            index = m.end()
        else:
            raise SyntaxError("Bad char {}".format(text[index]))


if __name__ == "__main__":
    pat = re.compile(master)
    text = "for x"
    for m in tokenizer(pat, text):
        tokname, tokvalue = (m.lastgroup, m.group())
        # ensure this token isn't a reserved word
        if tokname == 'ID':
            tokname = KEYWORDS.get(tokvalue, "ID")
        print((tokname, tokvalue))
