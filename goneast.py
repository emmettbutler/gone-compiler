class AST(object):
    '''
    Base class for all of the AST nodes.  Each node is expected to
    define the _fields attribute which lists the names of stored
    attributes.   The __init__() method below takes positional
    arguments and assigns them to the appropriate fields.  Any
    additional arguments specified as keywords are also assigned.
    '''
    _fields = []

    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __repr__(self):
        attrs = [(a, str(getattr(self, a))) for a in self.__dir__()
                 if not a.startswith('_') and a != 'lineno' and not isinstance(getattr(self, a), AST)
                 and not isinstance(getattr(self, a), list) and getattr(self, a) is not None]
        return "{}: {}".format(self.__class__.__name__, ", ".join(["{}: {}".format(a[0], a[1]) for a in attrs]))


class Program(AST):
    '''
    statements | empty
    '''
    _fields = ['statements']


class Statements(AST):
    '''
    statements | statement
    '''
    _fields = ['statements']


class Location(AST):
    '''
    ID
    '''
    _fields = ['name']


class UnaryOp(AST):
    '''
    PLUS expression | MINUS expression
    '''
    _fields = ['operator', 'expr']


class BinOp(AST):
    '''
    expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    '''
    _fields = ['left', 'operator', 'right']


class ComparisonBinOp(AST):
    _fields = ['left', 'operator', 'right']


class BooleanUnaryOp(AST):
    _fields = ['operator', 'expr']


class ExpressionGrouping(AST):
    '''
    LPAREN expression RPAREN
    '''
    _fields = ['expr']


class ConstDeclaration(AST):
    '''
    CONST ID ASSIGN expression SEMI
    '''
    _fields = ['name', 'expr']


class VarDeclaration(AST):
    '''
    VAR ID typename SEMI
    '''
    _fields = ['name', 'typename']


class VarDeclarationAssignment(AST):
    '''
    VAR ID typename ASSIGN expression SEMI
    '''
    _fields = ['name', 'typename', 'expr']


class AssignmentStatement(AST):
    '''
    location ASSIGN expression SEMI
    '''
    _fields = ['name', 'expr']


class ExpressionList(AST):
    '''
    exprlist COMMA expression
    '''
    _fields = ['expressions']


class NamedExpressionList(AST):
    '''
    ID LPAREN exprlist RPAREN
    '''
    _fields = ['name', 'exprlist']


class ExternDeclaration(AST):
    '''
    EXTERN func_prototype SEMI
    '''
    _fields = ['prototype']


class ReturnStatement(AST):
    _fields = ['expr']


class FunctionDefinition(AST):
    _fields = ['prototype', 'block']


class FunctionPrototype(AST):
    '''
    FUNC ID LPAREN parameters RPAREN typename
    '''
    _fields = ['name', 'params', 'typename']


class Parameters(AST):
    '''
    parameters COMMA parm_declaration
    '''
    _fields = ['parameters']


class ParameterDeclaration(AST):
    '''
    ID typename
    '''
    _fields = ['name', 'typename']


class PrintStatement(AST):
    '''
    print expression ;
    '''
    _fields = ['expr']


class Literal(AST):
    '''
    A literal value such as 2, 2.5, or "two"
    '''
    _fields = ['value']


class WhileStatement(AST):
    _fields = ['expr', 'statements']


class ConditionalStatement(AST):
    _fields = ['expr', 'true_statements', 'false_statements']


class NodeVisitor(object):
    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None

    def generic_visit(self, node):
        '''
        Method executed if no applicable visit_ method can be found.
        This examines the node to see if it has _fields, is a list,
        or can be further traversed.
        '''
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)


class NodeTransformer(NodeVisitor):
    '''
    Class that allows nodes of the parse tree to be replaced/rewritten.
    This is determined by the return value of the various visit_() functions.
    If the return value is None, a node is deleted. If any other value is returned,
    it replaces the original node.

    The main use of this class is in code that wants to apply transformations
    to the parse tree.  For example, certain compiler optimizations or
    rewriting steps prior to code generation.
    '''
    def generic_visit(self, node):
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                newvalues = []
                for item in value:
                    if isinstance(item, AST):
                        newnode = self.visit(item)
                        if newnode is not None:
                            newvalues.append(newnode)
                    else:
                        newvalues.append(n)
                value[:] = newvalues
            elif isinstance(value, AST):
                newnode = self.visit(value)
                if newnode is None:
                    delattr(node, field)
                else:
                    setattr(node, field, newnode)
        return node


# DO NOT MODIFY
def flatten(top):
    '''
    Flatten the entire parse tree into a list for the purposes of
    debugging and testing.  This returns a list of tuples of the
    form (depth, node) where depth is an integer representing the
    parse tree depth and node is the associated AST node.
    '''
    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []

        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
