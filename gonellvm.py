# gonellvm.py
'''
Project 5 : Generate LLVM
=========================
In this project, you're going to translate the SSA intermediate code
into LLVM IR.    Once you're done, your code will be runnable.  It
is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.   Don't rush into it.

The basic idea of this project is exactly the same as the interpreter
in Project 4.   You'll make a class that walks through the instruction
sequence and triggers a method for each kind of instruction.  Instead
of running the instruction however, you'll be generating LLVM
instructions.

Further instructions are contained in the comments.
'''

# LLVM imports. Don't change this.
from llvm.core import Module, Builder, Function, Type, Constant, GlobalVariable

# Declare the LLVM type objects that you want to use for the types
# in our intermediate code.  Basically, you're going to need to
# declare your integer, float, and string types here.

int_type = Type.int()         # 32-bit integer
float_type = Type.double()      # 64-bit float
string_type = None               # Up to you (leave until the end)

# A dictionary that maps the typenames used in IR to the corresponding
# LLVM types defined above.   This is mainly provided for convenience
# so you can quickly look up the type object given its type name.
typemap = {
    'int': int_type,
    'float': float_type,
    'string': string_type
}

# The following class is going to generate the LLVM instruction stream.
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution module is very similar
# to the interpreter written in Project 4.  See specific comments
# in the class.


class GenerateLLVM(object):
    def __init__(self, name="module"):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A Function instance in which to insert code
        #    3.  A Builder instance to generate instructions
        #
        # Note: at this point in the project, we don't have any user-defined
        # functions so we're just going to emit all LLVM code into a top
        # level function void main() { ... }.   This will get changed later.

        self.module = Module.new(name)
        self.function = Function.new(self.module,
                                     Type.function(Type.void(), [], False),
                                     "main")
        self.block = self.function.append_basic_block('entry')
        self.builder = Builder.new(self.block)

        # Dictionary that holds all of the global variable/function declarations.
        # Any declaration in the Gone source code is going to get an entry here
        self.vars = {}

        # Dictionary that holds all of the temporary variables created in
        # the intermediate code.   For example, if you had an expression
        # like this:
        #
        #      a = b + c*d
        #
        # The corresponding intermediate code might look like this:
        #
        #      ('load_int', 'b', 'int_1')
        #      ('load_int', 'c', 'int_2')
        #      ('load_int', 'd', 'int_3')
        #      ('mul_int', 'int_2','int_3','int_4')
        #      ('add_int', 'int_1','int_4','int_5')
        #      ('store_int', 'int_5', 'a')
        #
        # The self.temp dictionary below is used to map names such as 'int_1',
        # 'int_2' to their corresponding LLVM values.  Essentially, every time
        # you make anything in LLVM, it gets stored here.
        self.temps = {}

        # Initialize the runtime library functions (see below)
        self.declare_runtime_library()

    def declare_runtime_library(self):
        # Certain functions such as I/O and string handling are often easier
        # to implement in an external C library.  This method should make
        # the LLVM declarations for any runtime functions to be used
        # during code generation.    Please note that runtime function
        # functions are implemented in C in a separate file gonert.c

        self.runtime = {}

        # Declare printing functions
        self.runtime['_print_int'] = Function.new(self.module,
                                                  Type.function(Type.void(), [int_type], False),
                                                  "_print_int")

        self.runtime['_print_float'] = Function.new(self.module,
                                                    Type.function(Type.void(), [float_type], False),
                                                    "_print_float")

    def generate_code(self, ircode):
        # Given a sequence of SSA intermediate code tuples, generate LLVM
        # instructions using the current builder (self.builder).  Each
        # opcode tuple (opcode, args) is dispatched to a method of the
        # form self.emit_opcode(args)
        for op in ircode.code:
            opcode = op[0]
            print(opcode)
            if hasattr(self, "emit_" + opcode):
                getattr(self, "emit_" + opcode)(*op[1:])
            else:
                print("Warning: No emit_" + opcode + "() method")

        # Add a return statement.  Note, at this point, we don't really have
        # user-defined functions so this is a bit of hack--it may be removed later.
        self.builder.ret_void()

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_literal_int(self, value, target):
        self.temps[target] = Constant.int(int_type, value)

    def emit_literal_float(self, value, target):
        self.temps[target] = Constant.real(float_type, value)

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_alloc_int(self, name):
        var = GlobalVariable.new(self.module, int_type, name)
        var.initializer = Constant.int(int_type, 0)
        self.vars[name] = var

    def emit_alloc_float(self, name):
        var = GlobalVariable.new(self.module, float_type, name)
        var.initializer = Constant.real(float_type, 0.0)
        self.vars[name] = var

    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_load_int(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_float(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_store_int(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_float(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    # Binary + operator
    def emit_add_int(self, left, right, target):
        self.temps[target] = self.builder.add(self.temps[left], self.temps[right], target)

    def emit_add_float(self, left, right, target):
        self.temps[target] = self.builder.fadd(self.temps[left], self.temps[right], target)

    # Binary - operator
    def emit_sub_int(self, left, right, target):
        self.temps[target] = self.builder.sub(self.temps[left], self.temps[right], target)

    def emit_sub_float(self, left, right, target):
        self.temps[target] = self.builder.fsub(self.temps[left], self.temps[right], target)

    # Binary * operator
    def emit_mul_int(self, left, right, target):
        self.temps[target] = self.builder.mul(self.temps[left], self.temps[right], target)

    def emit_mul_float(self, left, right, target):
        self.temps[target] = self.builder.fmul(self.temps[left], self.temps[right], target)

    # Binary / operator
    def emit_div_int(self, left, right, target):
        self.temps[target] = self.builder.sdiv(self.temps[left], self.temps[right], target)

    def emit_div_float(self, left, right, target):
        self.temps[target] = self.builder.fdiv(self.temps[left], self.temps[right], target)

    # Unary + operator
    def emit_uadd_int(self, source, target):
        self.temps[target] = self.builder.add(
            Constant.int(int_type, 0),
            self.temps[source],
            target)

    def emit_uadd_float(self, source, target):
        self.temps[target] = self.builder.fadd(
            Constant.real(float_type, 0.0),
            self.temps[source],
            target)

    # Unary - operator
    def emit_usub_int(self, source, target):
        self.temps[target] = self.builder.mul(
            Constant.int(int_type, -1),
            self.temps[source],
            target)

    def emit_usub_float(self, source, target):
        self.temps[target] = self.builder.fmul(
            Constant.real(float_type, -1.0),
            self.temps[source],
            target)

    # Print statements
    def emit_print_int(self, source):
        self.builder.call(self.runtime['_print_int'], [self.temps[source]])

    def emit_print_float(self, source):
        self.builder.call(self.runtime['_print_float'], [self.temps[source]])

    # Extern function declaration.
    def emit_extern_func(self, name, rettypename, *parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = Type.function(rettype, parmtypes, False)
        self.vars[name] = Function.new(self.module, func_type, name)

    # Call an external function.
    def emit_call_func(self, funcname, target, *funcargs):
        resolved_args = []
        for arg in funcargs:
            resolved_args.append(self.temps[arg])
        self.temps[target] = self.builder.call(self.vars[funcname], resolved_args)

#######################################################################
#                 DO NOT MODIFY ANYTHING BELOW HERE
#######################################################################


def main():
    import gonelex
    import goneparse
    import gonecheck
    import gonecode
    import sys
    import ctypes
    from errors import subscribe_errors, errors_reported
    from llvm.ee import ExecutionEngine

    # Load the Gone runtime library (see Makefile)
    ctypes._dlopen('./gonert.so', ctypes.RTLD_GLOBAL)

    lexer = gonelex.make_lexer()
    parser = goneparse.make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse(open(sys.argv[1]).read())
        # Check the program
        gonecheck.check_program(program)
        # If no errors occurred, generate code
        if not errors_reported():
            code = gonecode.generate_code(program)
            # Emit the code sequence
            g = GenerateLLVM()
            g.generate_code(code)
            print(g.module)

            # Verify and run function that was created during code generation
            print(":::: RUNNING ::::")
            g.function.verify()
            llvm_executor = ExecutionEngine.new(g.module)
            llvm_executor.run_function(g.function, [])

if __name__ == '__main__':
    main()
