from errors import error
from ply.lex import lex

tokens = [
    'ID', 'CONST', 'VAR', 'PRINT', 'FUNC', 'EXTERN',

    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'ASSIGN', 'SEMI', 'LPAREN', 'RPAREN',
    'COMMA',

    'INTEGER', 'FLOAT', 'STRING', 'BOOL',

    'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQ', 'AND', 'OR', 'NOT',

    'IF', 'ELSE', 'WHILE', 'LBRACE', 'RBRACE'
]

t_ignore = ' \t\r'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_SEMI = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_EQ = r'=='
t_NEQ = r'!='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'
t_LBRACE = r'\{'
t_RBRACE = r'\}'


def t_FLOAT(t):
    r'(([0-9]*\.[0-9]*([eE][+-]?1)?)|([0-9]*[eE][+-]?1))'
    t.value = float(t.value)               # Conversion to Python float
    return t


def t_BOOL(t):
    r'(true|false)'
    t.value = True if t.value == "true" else False
    return t


def t_INTEGER(t):
    r'[0-9]+'
    # Conversion to a Python int
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'(").*?(")'
    # Strip off the leading/trailing quotes
    t.value = t.value[1:-1]

    # If you are going to replace the string escape codes, do it here
    t.value = t.value.replace("\\\\", "\\")
    t.value = t.value.replace("\\n", "\n")

    return t


def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'

    reserved = {
        'const': 'CONST',
        'var': 'VAR',
        'print': 'PRINT',
        'func': 'FUNC',
        'extern': 'EXTERN',
        'true': 'BOOL',
        'false': 'BOOL',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE'
    }

    if t.value in reserved:
        t.type = reserved.get(t.value)

    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# C-style comment (/* ... */)
def t_COMMENT(t):
    r'(/\*)(.|\n)*?(\*/)'

    # Must count the number of newlines included to keep line count accurate
    t.lexer.lineno += t.value.count('\n')


# C++-style comment (//...)
def t_CPPCOMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1


def t_error(t):
    error(t.lexer.lineno, "Illegal character %r" % t.value[0])
    t.lexer.skip(1)


# Unterminated C-style comment
def t_COMMENT_UNTERM(t):
    r'(/\*)(.|\n)*'
    error(t.lexer.lineno, "Unterminated comment")


# Unterminated string literal
def t_STRING_UNTERM(t):
    r'".*'
    error(t.lexer.lineno, "Unterminated string literal")
    t.lexer.lineno += 1


def make_lexer():
    '''
    Utility function for making the lexer object
    '''
    return lex()


def main():
    import sys
    from errors import subscribe_errors

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s filename\n" % sys.argv[0])
        raise SystemExit(1)

    lexer = make_lexer()
    with subscribe_errors(lambda msg: sys.stderr.write(msg + "\n")):
        lexer.input(open(sys.argv[1]).read())
        for tok in iter(lexer.token, None):
            sys.stdout.write("%s\n" % tok)

if __name__ == '__main__':
    main()
