class BlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''
    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block


class BaseLLVMBlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''
    def __init__(self):
        self.visited_blocks = set()

    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name) and block not in self.visited_blocks:
                getattr(self, name)(block)
                self.visited_blocks |= {block}
            block = block.next_block


class EmitBlocksVisitor(BlockVisitor):
    def visit_BasicBlock(self, block):
        print("Block:[%s]" % block)
        for inst in block.instructions:
            print("    %s" % (inst,))

    def visit_ConditionalBlock(self, block):
        self.visit_BasicBlock(block)
        # Emit a conditional jump around the if-branch
        inst = ('JUMP_IF_FALSE',
                block.false_branch if block.false_branch else block.next_block)
        print("    %s" % (inst,))
        self.visit(block.true_branch)
        if block.false_branch:
            # Emit a jump around the else-branch (if there is one)
            inst = ('JUMP', block.next_block)
            print("    %s" % (inst,))
            self.visit(block.false_branch)

    def visit_WhileBlock(self, block):
        self.visit_BasicBlock(block)
        # Emit a conditional jump around the if-branch
        inst = ('JUMP_IF_FALSE', block.next_block)
        print("    %s" % (inst,))
        self.visit(block.loop_branch)


class Block(object):
    def __init__(self):
        self.instructions = []   # Instructions in the block
        self.next_block = None    # Link to the next block

    def append(self,instr):
        self.instructions.append(instr)

    def __iter__(self):
        return iter(self.instructions)


class BasicBlock(Block):
    '''
    Class for a simple basic block.  Control flow unconditionally
    flows to the next block.
    '''
    pass


class ConditionalBlock(Block):
    '''
    Class for a basic-block representing an if-else.  There are
    two branches to handle each possibility.
    '''
    def __init__(self, testvar=None):
        super(ConditionalBlock,self).__init__()
        self.testvar = testvar
        self.true_branch = None
        self.false_branch = None


class WhileBlock(Block):
    def __init__(self):
        super(WhileBlock, self).__init__()
        self.loop_branch = None
