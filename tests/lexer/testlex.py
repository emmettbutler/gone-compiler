# testlex.py

import unittest
import gonelex

# Make the lexer object
lexer = gonelex.make_lexer()


class TestLexer(unittest.TestCase):
    def test_symbols(self):
        lexer.input('+ - * / ( ) = , ;')
        toks = list(iter(lexer.token, None))
        self.assertEqual(
            [t.type for t in toks],
            ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
             'ASSIGN', 'COMMA', 'SEMI'])

    def test_keywords(self):
        lexer.input('const var print func extern')
        toks = list(iter(lexer.token, None))
        self.assertEqual(
            [t.type for t in toks],
            ['CONST', 'VAR', 'PRINT', 'FUNC', 'EXTERN'])

    def test_identifiers(self):
        lexer.input('a z  A Z _a _z _A _Z a123 A123 a123z A123Z')
        toks = list(iter(lexer.token, None))
        self.assertTrue(all(t.type == 'ID' for t in toks))
        self.assertEqual(
            [t.value for t in toks],
            ['a', 'z', 'A', 'Z', '_a', '_z', '_A', '_Z',
             'a123', 'A123', 'a123z', 'A123Z'])

    def test_integers(self):
        lexer.input('12345 0123')
        toks = list(iter(lexer.token, None))
        self.assertTrue(all(t.type == 'INTEGER' for t in toks))
        self.assertEqual(
            [t.value for t in toks],
            [12345, 123])

    def test_floats(self):
        lexer.input('1.23 1.23e1 1.23e+1 1.23e-1 123e1 123. .123 0. .0 1.23E1 1.23E+1')
        toks = list(iter(lexer.token, None))
        self.assertTrue(all(t.type == 'FLOAT' for t in toks))
        self.assertEqual(
            [t.value for t in toks],
            [1.23, 1.23e1, 1.23e+1, 1.23e-1, 123e1, 123., .123, 0., .0, 1.23E1, 1.23E+1])

    def test_strings(self):
        lexer.input('"hello world"')
        toks = list(iter(lexer.token, None))
        self.assertTrue(all(t.type == 'STRING' for t in toks))
        self.assertEqual(
            [t.value for t in toks],
            ['hello world'])


if __name__ == '__main__':
    unittest.main()
