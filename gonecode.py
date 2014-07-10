import goneast
from goneblock import BasicBlock, ConditionalBlock, WhileBlock, EmitBlocksVisitor
from collections import defaultdict

# STEP 1: Map map operator symbol names such as +, -, *, /
# to actual opcode names 'add','sub','mul','div' to be emitted in
# the SSA code.   This is easy to do using dictionaries:

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

# STEP 2: Implement the following Node Visitor class so that it creates
# a sequence of SSA instructions in the form of tuples.  Use the
# above description of the allowed op-codes as a guide.


class GenerateCode(goneast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''
    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.versions = defaultdict(int)

        # The generated code (list of tuples)
        self.current_block = BasicBlock()
        self.start_block = self.current_block

        # A list of external declarations (and types)
        self.externs = []

    def pprint(self, code):
        print("code:")
        for a in code:
            print(a)

    def new_temp(self, typeobj):
        '''
        Create a new temporary variable of a given type.
        '''
        name = "__%s_%d" % (typeobj.name, self.versions[typeobj.name])
        self.versions[typeobj.name] += 1
        return name

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.current_block list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names of the AST nodes you've defined.

    def visit_Program(self, node):
        for statement in node.statements.statements:
            #print(statement)
            self.visit(statement)

    def visit_VarDeclarationAssignment(self, node):
        inst = ('alloc_' + node.type_obj.name, node.name)
        self.current_block.append(inst)

        self.visit(node.expr)

        inst = ('store_' + node.type_obj.name, node.expr.gen_location, node.name)
        self.current_block.append(inst)

    def visit_VarDeclaration(self, node):
        inst = ('alloc_' + node.type_obj.name, node.name)
        self.current_block.append(inst)

        target = self.new_temp(node.type_obj)

        # make a default value for declarations without definitions
        inst = ('literal_' + node.type_obj.name, node.type_obj.default, target)
        self.current_block.append(inst)

        inst = ('store_' + node.type_obj.name, target, node.name)
        self.current_block.append(inst)

    def visit_ConstDeclaration(self, node):
        inst = ('alloc_' + node.type_obj.name, node.name)
        self.current_block.append(inst)

        self.visit(node.expr)

        inst = ('store_' + node.type_obj.name, node.expr.gen_location, node.name)
        self.current_block.append(inst)

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


# STEP 3: Testing
#
# Try running this program on the input file Project4/Tests/good.g and viewing
# the resulting SSA code sequence.
#
#     bash % python gonecode.py good.g
#     ... look at the output ...
#
# Sample output can be found in Project4/Tests/good.out.  While coding,
# you may want to break the code down into more manageable chunks.
# Think about unit testing.

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------


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
