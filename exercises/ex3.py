import ast


class TypeDefinition(object):
    def __init__(self, name, bin_ops, unary_ops):
        self.name = name
        self.bin_ops = bin_ops
        self.unary_ops = unary_ops

num_type = TypeDefinition("num", {'Add', 'Sub', 'Mult', 'Div'}, {'UAdd', 'USub'})
str_type = TypeDefinition("str", {'Add'}, set())


class TypeCheck(ast.NodeVisitor):
    def __init__(self):
        self.symtab = {}

    def visit_Num(self, node):
        node.check_type = num_type

    def visit_Str(self, node):
        node.check_type = str_type

    def visit_Assign(self, node):
        self.visit(node.value)
        check_type = getattr(node.value, "check_type", None)
        # Store known type information in the symbol table (if any)
        for target in node.targets:
            self.symtab[target.id] = check_type

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            # Check if any type information is known.  If so, attach it
            if node.id in self.symtab:
                check_type = self.symtab[node.id]
                if check_type:
                    node.check_type = check_type
            else:
                print("Undefined identifier %s" % node.id)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        opname = node.op.__class__.__name__
        if hasattr(node.left, "check_type") and hasattr(node.right, "check_type"):
            if node.left.check_type != node.right.check_type:
                print("Type Error: %s %s %s" % (node.left.check_type,
                                                opname,
                                                node.right.check_type))
            elif opname not in node.left.check_type.bin_ops:
                print("Unsupported binary operation %s for type %s" % (opname, node.left.check_type.name))
            else:
                node.check_type = node.left.check_type

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        opname = node.op.__class__.__name__
        if hasattr(node.operand, "check_type"):
            if opname not in node.operand.check_type.unary_ops:
                print("Unsupported unary operation %s for type %s" % (opname, node.operand.check_type.name))
            else:
                node.check_type = node.operand.check_type


code = """\
a = 23
b = 45
c = "Hello"
d = a + 20*b - 13
"""
checker = TypeCheck()
checker.visit(ast.parse(code))
print(checker.symtab)
