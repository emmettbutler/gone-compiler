import goneast
from goneblock import BasicBlock, ConditionalBlock, WhileBlock, EmitBlocksVisitor
from collections import defaultdict

binary_ops = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '<': 'lt',
    '>': 'gt',
    '<=': 'lte',
    '>=': 'gte',
    '==': 'eq',
    '!=': 'neq',
    '&&': 'and',
    '||': 'or'
}

unary_ops = {
    '+': 'uadd',
    '-': 'usub',
    '!': 'not'
}


class GenerateCode(goneast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()
        self.versions = defaultdict(int)
        self.current_block = BasicBlock()
        self.start_block = self.current_block
        self.externs = []
        self.functions = {}
        self.in_function = False
        self.functions['@main'] = (self.start_block, None)

    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            if not self.in_function:
                self.current_block = self.start_block
            return visitor(node)
        else:
            return None

    def new_temp(self, typeobj):
        '''
        Create a new temporary variable of a given type.
        '''
        name = "__%s_%d" % (typeobj.name, self.versions[typeobj.name])
        self.versions[typeobj.name] += 1
        return name

    def visit_Program(self, node):
        self.visit(node.statements)

    def visit_Statements(self, node):
        for statement in node.statements:
            self.visit(statement)

    def _declaration_helper(self, node):
        alloc_base = "global" if node.scope == "global" else "alloc"
        inst = (alloc_base + '_' + node.type_obj.name, node.name)
        self.current_block.append(inst)

        if hasattr(node, 'expr'):
            self.visit(node.expr)
            inst = ('store_' + node.type_obj.name, node.expr.gen_location, node.name)
            self.current_block.append(inst)
        else:
            target = self.new_temp(node.type_obj)

            # make a default value for declarations without definitions
            inst = ('literal_' + node.type_obj.name, node.type_obj.default, target)
            self.current_block.append(inst)

            inst = ('store_' + node.type_obj.name, target, node.name)
            self.current_block.append(inst)

    def visit_ParameterDeclaration(self, node):
        self._declaration_helper(node)

    def visit_VarDeclarationAssignment(self, node):
        self._declaration_helper(node)

    def visit_ConstDeclaration(self, node):
        self._declaration_helper(node)

    def visit_VarDeclaration(self, node):
        self._declaration_helper(node)

    def visit_AssignmentStatement(self, node):
        self.visit(node.expr)

        inst = ('store_' + node.expr.type_obj.name, node.expr.gen_location, node.name)
        self.current_block.append(inst)

    def visit_ExternDeclaration(self, node):
        self.visit(node.prototype)

        inst = ['extern_func', node.prototype.name]
        inst.append(node.prototype.typename)
        for arg in node.prototype.argtypes:
            inst.append(arg.name)
        self.current_block.append(tuple(inst))

    def visit_FunctionPrototype(self, node):
        self.visit(node.params)
        node.argtypes = []
        for parameter in node.params.parameters:
            node.argtypes.append(parameter.type_obj)

    def visit_Literal(self, node):
        # Create a new temporary variable name
        target = self.new_temp(node.type_obj)

        # Make the SSA opcode and append to list of generated instructions
        inst = ('literal_' + node.type_obj.name, node.value, target)
        self.current_block.append(inst)

        # Save the name of the temporary variable where the value was placed
        node.gen_location = target

    def visit_Location(self, node):
        target = self.new_temp(node.type_obj)

        inst = ('load_' + node.type_obj.name, node.name, target)
        self.current_block.append(inst)

        node.gen_location = target

    def _visit_UnaryOp_helper(self, node):
        self.visit(node.expr)

        target = self.new_temp(node.type_obj)

        opcode = unary_ops[node.operator] + "_" + node.expr.type_obj.name
        inst = (opcode, node.expr.gen_location, target)
        self.current_block.append(inst)

        node.gen_location = target

    def visit_UnaryOp(self, node):
        self._visit_UnaryOp_helper(node)

    def visit_BooleanUnaryOp(self, node):
        self._visit_UnaryOp_helper(node)

    def _visit_BinOp_helper(self, node):
        self.visit(node.left)
        self.visit(node.right)

        target = self.new_temp(node.type_obj)

        opcode = binary_ops[node.operator] + "_" + node.left.type_obj.name
        inst = (opcode, node.left.gen_location, node.right.gen_location, target)
        self.current_block.append(inst)

        node.gen_location = target

    def visit_BinOp(self, node):
        self._visit_BinOp_helper(node)

    def visit_ComparisonBinOp(self, node):
        self._visit_BinOp_helper(node)

    def visit_NamedExpressionList(self, node):
        self.visit(node.exprlist)

        target = self.new_temp(node.type_obj)

        inst = ['call_func', node.name]
        inst.append(target)
        for arg in node.exprlist.expressions:
            inst.append(arg.gen_location)
        self.current_block.append(tuple(inst))

        node.gen_location = target

    def visit_ExpressionGrouping(self, node):
        self.visit(node.expr)

        node.gen_location = node.expr.gen_location

    def visit_PrintStatement(self, node):
        # Visit the printed expression
        self.visit(node.expr)

        # Create the opcode and append to list
        inst = ('print_' + node.expr.type_obj.name, node.expr.gen_location)
        self.current_block.append(inst)

    def visit_ConditionalStatement(self, node):
        cond_block = ConditionalBlock()
        self.current_block.next_block = cond_block
        self.current_block = cond_block

        self.visit(node.expr)
        cond_block.testvar = node.expr.gen_location

        self.current_block = BasicBlock()
        cond_block.true_branch = self.current_block

        self.visit(node.true_statements)

        if node.false_statements is not None:
            self.current_block = BasicBlock()
            cond_block.false_branch = self.current_block

            self.visit(node.false_statements)

        self.current_block = BasicBlock()
        cond_block.next_block = self.current_block

    def visit_WhileStatement(self, node):
        cond_block = WhileBlock()
        self.current_block.next_block = cond_block
        self.current_block = cond_block

        self.visit(node.expr)
        cond_block.testvar = node.expr.gen_location

        self.current_block = BasicBlock()
        cond_block.loop_branch = self.current_block

        self.visit(node.statements)

        self.current_block = BasicBlock()
        cond_block.next_block = self.current_block

    def visit_FunctionDefinition(self, node):
        self.in_function = True
        func_block = BasicBlock()
        self.current_block.next_block = func_block
        self.current_block = func_block

        self.visit(node.prototype)
        self.visit(node.block)

        self.functions[node.prototype.name] = (func_block, node)
        self.in_function = False


def generate_code(node):
    '''
    Generate SSA code from the supplied AST node.
    '''
    gen = GenerateCode()
    gen.visit(node)
    return gen


def main():
    import gonelex
    import goneparse
    import gonecheck
    import sys
    from errors import subscribe_errors, errors_reported
    lexer = gonelex.make_lexer()
    parser = goneparse.make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse(open(sys.argv[1]).read())
        # Check the program
        gonecheck.check_program(program)
        # If no errors occurred, generate code
        if not errors_reported():
            code = generate_code(program)
            code = EmitBlocksVisitor().visit(code.start_block)

if __name__ == '__main__':
    main()
