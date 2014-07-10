class Interpreter(object):
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
            opname, typename = opcode.split("_")
            matches = [a for a in self.__dir__() if a.startswith("gen_" + opname + "_")]
            ran = False
            for match in matches:
                if typename in match.split("_")[2:]:
                    getattr(self, match)(*op[1:])
                    ran = True
                    break
            if not ran:
                if hasattr(self, "run_" + opcode):
                    getattr(self, "run_" + opcode)(*op[1:])
                else:
                    print("Warning: No run_" + opcode + "() method")

    def gen_alloc_int_float_string_bool(self, name):
        self.vars[name] = None

    def gen_store_int_float_string_bool(self, target, name):
        self.vars[name] = self.vars[target]

    def gen_load_int_float_string_bool(self, name, target):
        self.vars[target] = self.vars[name]

    def gen_sub_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] - self.vars[right]

    def gen_mul_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] * self.vars[right]

    def gen_div_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] / self.vars[right]

    def gen_add_int_float_string(self, left, right, target):
        self.vars[target] = self.vars[left] + self.vars[right]

    def gen_lt_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] < self.vars[right]

    def gen_gt_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] > self.vars[right]

    def gen_lte_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] <= self.vars[right]

    def gen_gte_int_float(self, left, right, target):
        self.vars[target] = self.vars[left] >= self.vars[right]

    def gen_eq_int_float_bool_string(self, left, right, target):
        self.vars[target] = self.vars[left] == self.vars[right]

    def gen_neq_int_float_bool_string(self, left, right, target):
        self.vars[target] = self.vars[left] != self.vars[right]

    def gen_and_bool(self, left, right, target):
        self.vars[target] = self.vars[left] and self.vars[right]

    def gen_or_bool(self, left, right, target):
        self.vars[target] = self.vars[left] or self.vars[right]

    def gen_uadd_int_float(self, source, target):
        self.vars[target] = self.vars[source]

    def gen_usub_int_float(self, source, target):
        self.vars[target] = -1 * self.vars[source]

    def gen_not_bool(self, source, target):
        self.vars[target] = not self.vars[source]

    def gen_literal_int_float_string_bool(self, value, target):
        self.vars[target] = value

    def gen_print_int_float_string(self, source):
        print(self.vars[source])

    def run_print_bool(self, source):
        print(str(self.vars[source]).lower())

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


def main():
    import gonelex
    import goneparse
    import gonecheck
    import gonecode
    import sys
    import time
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
            start = time.clock()
            interpreter.run(code.code)
            print(":::: FINISHED ::::")
            print("execution time: {0:.15f}s".format(time.clock() - start))


if __name__ == '__main__':
    main()
