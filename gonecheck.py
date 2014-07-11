from errors import error as _error
from goneast import *
import gonetype

from collections import ChainMap


RET_TYPE_SYMBOL = "%return_type"
HAS_RETURNED_SYMBOL = "%has_returned"


class SymbolTable(object):
    '''
    Class representing a symbol table.  It should provide functionality
    for adding and looking up nodes associated with identifiers.
    '''
    def __init__(self):
        self.table = ChainMap()
        self.current_scope = self.table
        self.root_scope = self.table
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
        self.current_scope[symbol] = data

    def get(self, symbol):
        if symbol in self.current_scope:
            return self.current_scope[symbol]
        return None

    def push_scope(self):
        self.current_scope = self.table.new_child()
        return self.current_scope

    def pop_scope(self):
        self.current_scope = self.current_scope.parents
        return self.current_scope

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
        _error(lineno, errstring)

    def visit_Program(self, node):
        self.visit(node.statements)

    def visit_Statements(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_PrintStatement(self, node):
        self.visit(node.expr)

    def visit_ConditionalStatement(self, node):
        self.visit(node.expr)
        if node.expr.type_obj != gonetype.bool_type:
            self.error(node.lineno, "expression in conditional of type {}, bool expected"
                .format(node.expr.type_obj.name))
        self.visit(node.true_statements)
        if node.false_statements is not None:
            self.visit(node.false_statements)

    def visit_WhileStatement(self, node):
        self.visit(node.expr)
        if node.expr.type_obj != gonetype.bool_type:
            self.error(node.lineno, "expression in while loop of type {}, bool expected"
                .format(node.expr.type_obj.name))
        self.visit(node.statements)

    def visit_UnaryOp(self, node):
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
        self.visit(node.left)
        self.visit(node.right)
        self._visit_BinOp_helper(node)

    def visit_ComparisonBinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        self._visit_BinOp_helper(node, override_type=gonetype.bool_type)

    def visit_BooleanUnaryOp(self, node):
        self.visit(node.expr)
        if node.expr.type_obj != gonetype.bool_type:
            self.error(node.lineno, "{} does not support unary {}"
                .format(node.expr.type_obj.name, node.operator))
        node.type_obj = gonetype.bool_type

    def visit_AssignmentStatement(self, node):
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
        self.visit(node.expr)
        symbol = self.symbol_table.get(node.name)
        if symbol is not None:
            self.error(node.lineno, "const '{}' is already defined".format(node.name))
            node.type_obj = gonetype.error_type
        else:
            node.type_obj = node.expr.type_obj
            self.symbol_table.add(node.name, node)
        node.ctx = "const"
        node.scope = "global" if self.symbol_table.current_scope == self.symbol_table.root_scope else "local"

    def visit_ReturnStatement(self, node):
        self.visit(node.expr)
        type_obj = self.symbol_table.get(RET_TYPE_SYMBOL)
        if type_obj != node.expr.type_obj:
            self.error(node.lineno, "invalid return type {}, {} expected"
                .format(node.expr.type_obj.name, type_obj.name))
        self.symbol_table.add(HAS_RETURNED_SYMBOL, True)

    def visit_FunctionDefinition(self, node):
        symbol = self.symbol_table.get(node.prototype.name)
        if symbol is not None:
            self.error(node.lineno, "symbol '{}' is already declared".format(node.name))
        else:
            self.symbol_table.add(node.prototype.name, node.prototype)
        self.symbol_table.push_scope()
        self.visit(node.prototype)
        node.type_obj = node.prototype.type_obj
        self.symbol_table.add(RET_TYPE_SYMBOL, node.type_obj)
        self.visit(node.block)
        if not self.symbol_table.get(HAS_RETURNED_SYMBOL):
            self.error(node.lineno, "no return statement found in function '{}'"
                .format(node.prototype.name))
        self.symbol_table.pop_scope()

    def _visit_VarDeclaration_helper(self, node):
        symbol = self.symbol_table.get(node.name)
        if symbol is not None:
            self.error(node.lineno, "symbol '{}' is already declared".format(node.name))
        else:
            self._set_node_type(node)
            self.symbol_table.add(node.name, node)
        node.ctx = "var"
        node.scope = "global" if self.symbol_table.current_scope == self.symbol_table.root_scope else "local"

    def visit_VarDeclaration(self, node):
        self._visit_VarDeclaration_helper(node)

    def visit_VarDeclarationAssignment(self, node):
        self.visit(node.expr)
        self._visit_VarDeclaration_helper(node)
        if node.expr.type_obj != node.type_obj:
            self.error(node.lineno, "cannot assign {} to {}"
                .format(node.expr.type_obj.name, node.type_obj.name))

    def visit_Location(self, node):
        symbol = self.symbol_table.get(node.name)
        if symbol is None or isinstance(symbol, gonetype.GoneType):
            self.error(node.lineno, "undeclared identifier '{}'".format(node.name))
            node.type_obj = gonetype.error_type
        elif symbol.__class__.__name__ not in ("VarDeclaration", "ConstDeclaration", "VarDeclarationAssignment", "ParameterDeclaration"):
            self.error(node.lineno, "identifier '{}' is not data".format(node.name))
            node.type_obj = gonetype.error_type
        else:
            node.type_obj = symbol.type_obj

    def visit_Literal(self, node):
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
        elif symbol.__class__.__name__ not in ("FunctionPrototype", "FunctionDefinition"):
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
        self._set_node_type(node)
        self.visit(node.params)
        node.argtypes = []
        for parameter in node.params.parameters:
            node.argtypes.append(parameter.type_obj)

    def visit_Parameters(self, node):
        for declaration in node.parameters:
            self.visit(declaration)

    def visit_ParameterDeclaration(self, node):
        self._set_node_type(node)
        self.symbol_table.add(node.name, node)
        node.scope = "local"

    def _set_node_type(self, node, typename=None):
        typename = node.typename if hasattr(node, 'typename') else typename
        type_obj = self.symbol_table.type_objects.get(typename, None)
        if type_obj is not None:
            node.type_obj = type_obj
        else:
            self.error(node.lineno, "unknown type name '{}'".format(typename))
            node.type_obj = gonetype.error_type


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
