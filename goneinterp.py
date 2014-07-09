# goneinterp.py
'''
Project 4 (Part 2) :  Write an Interpreter
==========================================

Once you've got your compiler emitting intermediate code, you should
be able to write a simple interpreter that runs the code.  This
can be useful for prototyping the execution environment, testing,
and other tasks involving the generated code.

Your task is simple, extend the Interpreter class below so that it
can run the code you generated in part 1.  The comments and docstrings
in the class describe it in further details.

When your done, you should be able to run simple programs by
typing:

    bash % python goneinterp.py someprogram.g
'''


class Interpreter(object):
    '''
    Runs an interpreter on the SSA intermediate code generated for
    your compiler.   The implementation idea is as follows.  Given
    a sequence of instruction tuples such as:

         code = [
              ('literal_int', 1, '_int_1'),
              ('literal_int', 2, '_int_2'),
              ('add_int', '_int_1', '_int_2, '_int_3')
              ('print_int', '_int_3')
              ...
         ]

    The class executes methods self.run_opcode(args).  For example:

             self.run_literal_int(1, '_int_1')
             self.run_literal_int(2, '_int_2')
             self.run_add_int('_int_1', '_int_2', '_int_3')
             self.run_print_int('_int_3')

    To store the values of variables created in the intermediate
    language, simply use a dictionary.

    For external function declarations, allow specific Python modules
    (e.g., math, os, etc.) to be registered with the interpreter.
    We don't have namespaces in the source language so this is going
    to be a bit of sick hack.
    '''
    def __init__(self, name="module"):
        # Dictionary of currently defined variables
        self.vars = {}

        # List of Python modules to search for external decls
        external_libs = ['math', 'os']
        self.external_libs = [__import__(a) for a in external_libs]

    def run(self, ircode):
        '''
        Run intermediate code in the interpreter.  ircode is a list
        of instruction tuples.  Each instruction (opcode, *args) is
        dispatched to a method self.run_opcode(*args)
        '''
        for op in ircode:
            opcode = op[0]
            if hasattr(self, "run_" + opcode):
                getattr(self, "run_" + opcode)(*op[1:])
            else:
                print("Warning: No run_" + opcode + "() method")

    # YOU MUST IMPLEMENT:  Methods for different opcodes.  A few sample
    # opcodes are shown below to get you started.

    def run_alloc_int(self, name):
        self.vars[name] = None

    def run_alloc_float(self, name):
        self.vars[name] = None

    def run_alloc_string(self, name):
        self.vars[name] = None

    def run_store_int(self, target, name):
        self.vars[name] = self.vars[target]

    def run_store_float(self, target, name):
        self.vars[name] = self.vars[target]

    def run_store_string(self, target, name):
        self.vars[name] = self.vars[target]

    def run_load_int(self, name, target):
        self.vars[target] = self.vars[name]

    def run_load_float(self, name, target):
        self.vars[target] = self.vars[name]

    def run_load_string(self, name, target):
        self.vars[target] = self.vars[name]

    def run_sub_int(self, left, right, target):
        self.vars[target] = self.vars[left] - self.vars[right]

    def run_sub_float(self, left, right, target):
        self.vars[target] = self.vars[left] - self.vars[right]

    def run_mul_int(self, left, right, target):
        self.vars[target] = self.vars[left] * self.vars[right]

    def run_mul_float(self, left, right, target):
        self.vars[target] = self.vars[left] * self.vars[right]

    def run_div_int(self, left, right, target):
        self.vars[target] = self.vars[left] / self.vars[right]

    def run_div_float(self, left, right, target):
        self.vars[target] = self.vars[left] / self.vars[right]

    def run_add_int(self, left, right, target):
        self.vars[target] = self.vars[left] + self.vars[right]

    def run_add_float(self, left, right, target):
        self.vars[target] = self.vars[left] + self.vars[right]

    def run_add_string(self, left, right, target):
        self.vars[target] = self.vars[left] + self.vars[right]

    def run_uadd_int(self, source, target):
        self.vars[target] = self.vars[source]

    def run_uadd_float(self, source, target):
        self.vars[target] = self.vars[source]

    def run_usub_int(self, source, target):
        self.vars[target] = -1 * self.vars[source]

    def run_usub_float(self, source, target):
        self.vars[target] = -1 * self.vars[source]

    def run_literal_int(self, value, target):
        self.vars[target] = value

    def run_literal_float(self, value, target):
        self.vars[target] = value

    def run_literal_string(self, value, target):
        self.vars[target] = value

    def run_print_int(self, source):
        print(self.vars[source])

    def run_print_float(self, source):
        print(self.vars[source])

    def run_print_string(self, source):
        print(self.vars[source])

    def run_extern_func(self, name, ret_type, *arg_types):
        found = False
        for lib in self.external_libs:
            if name in lib.__dict__:
                self.vars[name] = lib.__dict__[name]
                found = True
        if not found:
            raise RuntimeError("Error: extern '{}' not found".format(name))

    def run_call_func(self, name, target, *func_args):
        self.vars[target] = self.vars[name](*[self.vars[a] for a in func_args])

    # You must implement the rest of the operations below

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------


def main():
    import gonelex
    import goneparse
    import gonecheck
    import gonecode
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
            code = gonecode.generate_code(program)
            interpreter = Interpreter()
            interpreter.run(code.code)

if __name__ == '__main__':
    main()
