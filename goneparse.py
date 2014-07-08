# goneparse.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for the expression
language.  A formal BNF of the language follows.  Your task is to write
parsing rules and build the AST for this grammar using PLY.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  extern_declaration
          |  assign_statement
          |  print_statement

const_declaration : CONST ID = expression ;

var_declaration : VAR ID typename ;
                | VAR ID typename = expression ;

extern_declaration : EXTERN func_prototype ;

func_prototype : FUNC ID LPAREN parameters RPAREN typename

parameters : parameters , parm_declaration
           | parm_declaration
           | empty

parm_declaration : ID typename

assign_statement : location = expression ;

print_statement : PRINT expression ;

expression :  + expression
           |  - expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | ( expression )
           | ID ( exprlist )
           | location
           | literal

exprlist : | exprlist , expression
           | expression
           | empty

literal : INTEGER
        | FLOAT
        | STRING

location : ID

typename : ID

empty    :

To do the project, follow the instructions contained below.
'''

# ----------------------------------------------------------------------
# parsers are defined using PLYs yacc module.
#
# See http://www.dabeaz.com/ply/ply.html#ply_nn23
# ----------------------------------------------------------------------
from ply import yacc

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from errors import error

# ----------------------------------------------------------------------
# Get the token list defined in the lexer module.  This is required
# in order to validate and build the parsing tables.
from gonelex import tokens

# ----------------------------------------------------------------------
# Get the AST nodes.
# Read instructions in goneast.py
from goneast import *

# ----------------------------------------------------------------------
# Operator precedence table.   Operators must follow the same
# precedence rules as in Python.  Instructions to be given in the project.
# See http://www.dabeaz.com/ply/ply.html#ply_nn27

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UNARY')
)

# ----------------------------------------------------------------------
# YOUR TASK.   Translate the BNF in the doc string above into a collection
# of parser functions.  For example, a rule such as :
#
#   program : statements
#
# Gets turned into a Python function of the form:
#
# def p_program(p):
#      '''
#      program : statements
#      '''
#      p[0] = Program(p[1])
#
# For symbols such as '(' or '+', you'll need to replace with the name
# of the corresponding token such as LPAREN or PLUS.
#
# In the body of each rule, create an appropriate AST node and assign it
# to p[0] as shown above.
#
# For the purposes of lineno number tracking, you should assign a line number
# to each AST node as appropriate.  To do this, I suggest pulling the
# line number off of any nearby terminal symbol.  For example:
#
# def p_print_statement(p):
#     '''
#     print_statement: PRINT expr SEMI
#     '''
#     p[0] = PrintStatement(p[2],lineno=p.lineno(1))
#
#

# STARTING OUT
# ============
# The following grammar rules should give you an idea of how to start.
# Try running this file on the input Tests/parsetest0.e


def p_program(p):
    '''
    program : statements
            | empty
    '''
    p[0] = Program(p[1])


def p_empty(p):
    '''
    empty :
    '''


def p_statements(p):
    '''
    statements : statements statement
    '''
    p[0] = p[1]
    p[0].statements.append(p[2])


def p_statements_first(p):
    '''
    statements :  statement
    '''
    p[0] = Statements([p[1]])


def p_statement(p):
    '''
    statement : print_statement
              | const_declaration
              | var_declaration
              | assign_statement
              | extern_declaration
    '''
    p[0] = p[1]


def p_var_declaration(p):
    '''
    var_declaration : VAR ID typename SEMI
    '''
    p[0] = VarDeclaration(p[2], p[3])


def p_var_declaration_assignment(p):
    '''
    var_declaration : VAR ID typename ASSIGN expression SEMI
    '''
    p[0] = VarDeclarationAssignment(p[2], p[3], p[5])


def p_const_declaration(p):
    '''
    const_declaration : CONST ID ASSIGN expression SEMI
    '''
    p[0] = ConstDeclaration(p[2], p[4])


def p_extern_declaration(p):
    '''
    extern_declaration : EXTERN func_prototype SEMI
    '''
    p[0] = ExternDeclaration(p[2])


def p_func_prototype(p):
    '''
    func_prototype : FUNC ID LPAREN parameters RPAREN typename
    '''
    p[0] = FunctionPrototype(p[2], p[4], p[6])


def p_parameters(p):
    '''
    parameters : parameters COMMA parm_declaration
    '''
    p[0] = p[1]
    p[0].parameters.append(p[3])


def p_parameters_first(p):
    '''
    parameters : parm_declaration
    '''
    p[0] = Parameters([p[1]])


def p_parameters_empty(p):
    '''
    parameters : empty
    '''
    p[0] = Parameters([p[1]])


def p_parameter_declaration(p):
    '''
    parm_declaration : ID typename
    '''
    p[0] = ParameterDeclaration(p[1], p[2])


def p_assign_statement(p):
    '''
    assign_statement : location ASSIGN expression SEMI
    '''
    p[0] = AssignmentStatement(p[1], p[3])


def p_print_statemnt(p):
    '''
    print_statement : PRINT expression SEMI
    '''
    p[0] = PrintStatement(p[2])


def p_expression_literal(p):
    '''
    expression : literal
    '''
    p[0] = p[1]


def p_expression_location(p):
    '''
    expression : location
    '''
    p[0] = Location(p[1])


def p_location(p):
    '''
    location : ID
    '''
    p[0] = p[1]


def p_typename(p):
    '''
    typename : ID
    '''
    p[0] = p[1]


def p_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
    '''
    p[0] = BinOp(p[1], p[2], p[3])


def p_expression_unary(p):
    '''
    expression : PLUS expression %prec UNARY
               | MINUS expression %prec UNARY
    '''
    p[0] = UnaryOp(p[1], p[2])


def p_expression_parenlist(p):
    '''
    expression : ID LPAREN exprlist RPAREN
    '''
    p[0] = NamedExpressionList(p[1], p[3])


def p_exprlist(p):
    '''
    exprlist : exprlist COMMA expression
    '''
    p[0] = p[1]
    p[0].expressions.append(p[3])


def p_exprlist_first(p):
    '''
    exprlist : expression
    '''
    p[0] = ExpressionList([p[1]])


def p_exprlist_empty(p):
    '''
    exprlist : empty
    '''
    p[0] = ExpressionList([p[1]])


def p_expression_grouping(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = ExpressionGrouping(p[2])


def p_literal(p):
    '''
    literal : INTEGER
            | FLOAT
            | STRING
    '''
    p[0] = Literal(p[1], lineno=p.lineno(1))

# You need to implement the rest of the grammar rules here


# ----------------------------------------------------------------------
# DO NOT MODIFY
#
# catch-all error handling.   The following function gets called on any
# bad input.  See http://www.dabeaz.com/ply/ply.html#ply_nn31
def p_error(p):
    if p:
        error(p.lineno, "Syntax error in input at token '%s'" % p.value)
    else:
        error("EOF", "Syntax error. No more input.")

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------


def make_parser():
    parser = yacc.yacc()
    return parser


def main():
    import gonelex
    import sys
    from errors import subscribe_errors
    lexer = gonelex.make_lexer()
    parser = make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(program):
        print("%s%s" % (" " * (4 * depth), node))


if __name__ == '__main__':
    main()
