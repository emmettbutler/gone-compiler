# gonecheck.py
'''
Project 3 : Program Checking
============================
In this project you need to perform semantic checks on your program.
There are a few different aspects of doing this.

First, you will need to define a symbol table that keeps track of
previously declared identifiers.  The symbol table will be consulted
whenever the compiler needs to lookup information about variable and
constant declarations.

Next, you will need to define objects that represent the different
builtin datatypes and record information about their capabilities.
See the file gonetype.py.

Finally, you'll need to write code that walks the AST and enforces
a set of semantic rules.  Here is a complete list of everything you'll
need to check:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This includes variables,
    constants, and typenames.  For example, this kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

    Note: typenames such as "int", "float", and "string" are built-in names that
    should be defined at the start of the program.

2.  Types of literals

    All literal symbols must be assigned a type of "int", "float", or "string".
    For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = "forty";    // Type "string"

    To do this assignment, check the Python type of the literal value and attach
    a type name as appropriate.

3.  Binary operator type checking

    Binary operators only operate on operands of the same type and produce a
    result of the same type.   Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

4.  Unary operator type checking.

    Unary operators return a result that's the same type as the operand.

5.  Supported operators

    Here are the operators supported by each type:

    int:      binary { +, -, *, /}, unary { +, -}
    float:    binary { +, -, *, /}, unary { +, -}
    string:   binary { + }, unary { }

    Attempts to use unsupported operators should result in an error.
    For example:

        var string a = "Hello" + "World";     // OK
        var string b = "Hello" * "World";     // Error (unsupported op *)

6.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

    Values can only be assigned to variable declarations, not
    to constants.

For walking the AST, use the NodeVisitor class defined in goneast.py.
A shell of the code is provided below.
'''

from errors import error
from goneast import *
import gonetype


class SymbolTable(object):
    '''
    Class representing a symbol table.  It should provide functionality
    for adding and looking up nodes associated with identifiers.
    '''
    def __init__(self):
        self.table = {}
        self.type_objects = {
            int: gonetype.int_type,
            float: gonetype.float_type,
            str: gonetype.string_type,
            bool: gonetype.bool_type,
            'int': gonetype.int_type,
            'float': gonetype.float_type,
            'string': gonetype.string_type,
            'bool': gonetype.bool_type
        }

    def add(self, symbol, data):
        self.table[symbol] = data

    def get(self, symbol):
        return self.table.get(symbol, None)

    def pprint(self):
        print("{}top".format("-" * 10))
        for symbol in self.table:
            print("{}: {}".format(symbol, self.table.get(symbol)))
        print("-" * 10)


class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in goneast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.

    Note: You will need to adjust the names of the AST nodes if you
    picked different names.
    '''
    def __init__(self):
        # Initialize the symbol table
        self.symbol_table = SymbolTable()

        # Add built-in type names (int, float, string) to the symbol table
        self.symbol_table.add("int", gonetype.int_type)
        self.symbol_table.add("float", gonetype.float_type)
        self.symbol_table.add("string", gonetype.string_type)
        self.symbol_table.add("bool", gonetype.bool_type)

    def error(self, lineno, errstring):
        errstring = "Error: {}: {}".format(lineno, errstring)
        print(errstring)
        # raise SyntaxError(errstring)

    def visit_Program(self, node):
        # 1. Visit all of the statements
        # 2. Record the associated symbol table
        for statement in node.statements.statements:
            self.visit(statement)

    def visit_PrintStatement(self, node):
        self.visit(node.expr)

    def visit_UnaryOp(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type to the same as the operand
        self.visit(node.expr)
        if node.operator not in node.expr.type_obj.un_ops:
            self.error(node.lineno, "{} does not support unary {}"
                .format(node.expr.type_obj.name, node.operator))
        node.type_obj = node.expr.type_obj

    def _visit_BinOp_helper(self, node, override_type=None):
        if node.right.type_obj != node.left.type_obj:
            self.error(node.lineno, "cannot apply '{}' to '{}' and '{}'"
                .format(node.operator, node.left.type_obj.name, node.right.type_obj.name))
            node.type_obj = gonetype.error_type
        else:
            if override_type is not None:
                node.type_obj = override_type
            else:
                node.type_obj = node.right.type_obj
        if node.operator not in node.right.type_obj.bin_ops:
            if node.type_obj != gonetype.error_type:
                self.error(node.lineno, "{} does not support operator '{}'"
                    .format(node.right.type_obj.name, node.operator))

    def visit_BinOp(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type
        self.visit(node.left)
        self.visit(node.right)
        self._visit_BinOp_helper(node)

    def visit_ComparisonBinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        self._visit_BinOp_helper(node, override_type=gonetype.bool_type)

    def visit_AssignmentStatement(self, node):
        # 1. Make sure the location of the assignment is defined
        # 2. Check that assignment is allowed
        # 3. Check that the types match
        self.visit(node.expr)
        symbol = self.symbol_table.get(node.name)
        if symbol is None:
            self.error(node.lineno, "assigning to undeclared identifier '{}'"
                .format(node.name))
        elif symbol.type_obj != node.expr.type_obj:
            self.error(node.lineno, "cannot assign {} to {}".format(node.expr.type_obj.name, symbol.type_obj.name))
        if hasattr(symbol, 'ctx') and symbol.ctx == "const":
            self.error(node.lineno, "cannot assign to const '{}'".format(symbol.name))

    def visit_ExpressionGrouping(self, node):
        self.visit(node.expr)
        node.type_obj = node.expr.type_obj

    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table
        self.visit(node.expr)
        symbol = self.symbol_table.get(node.name)
        if symbol is not None:
            self.error(node.lineno, "const '{}' is already defined".format(node.name))
            node.type_obj = gonetype.error_type
        else:
            node.type_obj = node.expr.type_obj
            self.symbol_table.add(node.name, node)
        node.ctx = "const"

    def _visit_VarDeclaration_helper(self, node):
        symbol = self.symbol_table.get(node.name)
        if symbol is not None:
            self.error(node.lineno, "var '{}' is already declared".format(node.name))
        else:
            type_obj = self.symbol_table.type_objects.get(node.typename, None)
            if type_obj is not None:
                node.type_obj = type_obj
            else:
                self.error(node.lineno, "unknown type name '{}'".format(node.typename))
                node.type_obj = gonetype.error_type
            self.symbol_table.add(node.name, node)
        node.ctx = "var"

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 4. If there is no expression, set an initial value for the value
        self._visit_VarDeclaration_helper(node)

    def visit_VarDeclarationAssignment(self, node):
        # 3. Check that the type of the expression (if any) is the same
        self.visit(node.expr)
        self._visit_VarDeclaration_helper(node)
        if node.expr.type_obj != node.type_obj:
            self.error(node.lineno, "cannot assign {} to {}"
                .format(node.expr.type_obj.name, node.type_obj.name))

    def visit_Location(self, node):
        # 1. Make sure the location is a valid variable or constant value
        # 2. Assign the type of the location to the node
        symbol = self.symbol_table.get(node.name)
        if symbol is None or isinstance(symbol, gonetype.GoneType):
            self.error(node.lineno, "undeclared identifier '{}'".format(node.name))
            node.type_obj = gonetype.error_type
        elif not isinstance(symbol, VarDeclaration) and not isinstance(symbol, ConstDeclaration) and not isinstance(symbol, VarDeclarationAssignment):
            self.error(node.lineno, "identifier '{}' is not data".format(node.name))
            node.type_obj = gonetype.error_type
        else:
            node.type_obj = symbol.type_obj

    def visit_Literal(self, node):
        # Attach an appropriate type to the literal
        type_obj = self.symbol_table.type_objects.get(type(node.value), None)
        if type_obj is not None:
            node.type_obj = type_obj
        else:
            self.error("unsupported literal '{}'".format(node.value))
            node.type_obj = gonetype.error_type

    def visit_NamedExpressionList(self, node):
        self.visit(node.exprlist)
        symbol = self.symbol_table.get(node.name)
        if symbol is None or isinstance(symbol, gonetype.GoneType):
            self.error(node.lineno, "undefined function '{}'".format(node.name))
            node.type_obj = gonetype.error_type
        elif not isinstance(symbol, FunctionPrototype):
            self.error(node.lineno, "{} is not a function".format(node.name))
            node.type_obj = gonetype.error_type
        else:
            node.type_obj = symbol.type_obj
            if hasattr(symbol, 'argtypes'):
                if len(symbol.argtypes) != len(node.exprlist.expressions):
                    self.error(node.lineno, "function '{}' accepts {} arguments, {} given"
                        .format(node.name, len(symbol.argtypes),
                                len(node.exprlist.expressions)))
                for idx, (expression, expected_type) in enumerate(zip(node.exprlist.expressions, symbol.argtypes)):
                    if expression.type_obj != expected_type:
                        self.error(node.lineno, "argument {} to function '{}' is {}, {} expected"
                            .format(idx, node.name, expression.type_obj.name,
                                    expected_type.name))

    def visit_ExpressionList(self, node):
        for expression in node.expressions:
            self.visit(expression)

    def visit_ExternDeclaration(self, node):
        self.visit(node.prototype)
        self._visit_VarDeclaration_helper(node.prototype)

    def visit_FunctionPrototype(self, node):
        self.visit(node.params)
        node.argtypes = []
        for parameter in node.params.parameters:
            node.argtypes.append(parameter.type_obj)

    def visit_Parameters(self, node):
        for declaration in node.parameters:
            self.visit(declaration)

    def visit_ParameterDeclaration(self, node):
        type_obj = self.symbol_table.type_objects.get(node.typename, None)
        if type_obj is not None:
            node.type_obj = type_obj
        else:
            self.error(node.lineno, "unknown type name '{}'".format(node.typename))
            node.type_obj = gonetype.error_type

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------


def check_program(node):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(node)


def main():
    import gonelex
    import goneparse
    import sys
    from errors import subscribe_errors
    lexer = gonelex.make_lexer()
    parser = goneparse.make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse(open(sys.argv[1]).read())
        # Check the program
        check_program(program)


if __name__ == '__main__':
    main()
