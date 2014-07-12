from collections import ChainMap

from llvm.core import Module, Builder, Function, Type, Constant, GlobalVariable
from llvm.core import (
    FCMP_UEQ, FCMP_UGE, FCMP_UGT, FCMP_ULE, FCMP_ULT, FCMP_UNE,
    ICMP_EQ, ICMP_NE, ICMP_SGE, ICMP_SGT, ICMP_SLE, ICMP_SLT
)

from goneblock import BaseLLVMBlockVisitor

int_type = Type.int()
float_type = Type.double()
string_type = None
bool_type = Type.int(1)
void_type = Type.void()

args = None

typemap = {
    'int': int_type,
    'float': float_type,
    'string': string_type,
    'bool': bool_type,
    'void': void_type
}


class GenerateLLVMBlockVisitor(BaseLLVMBlockVisitor):
    def __init__(self):
        super(GenerateLLVMBlockVisitor, self).__init__()
        self.generator = GenerateLLVM()
        self.generator.declare_runtime_library()

    def visit_functions(self, toplevel_blocks):
        for name, start_block, ret_type, arg_types in toplevel_blocks:
            ret_type, arg_types = typemap[ret_type], [typemap[a] for a in arg_types]
            self.generator.make_function(name, ret_type, arg_types)

        for name, start_block, ret_type, arg_types in toplevel_blocks:
            self.generator.begin_function(name, ret_type, arg_types)
            self.visit(start_block)
            self.generator.end_function(name)

    def visit_BasicBlock(self, block, pred=None):
        self.generator.generate_code(block)

    def visit_ConditionalBlock(self, block):
        self.visit_BasicBlock(block)

        then_block = self.generator.add_block("then")
        else_block = self.generator.add_block("else")
        merge_block = self.generator.add_block("merge")

        self.generator.cbranch(block.testvar, then_block, else_block)

        self.generator.set_block(then_block)
        self.visit(block.true_branch)
        self.generator.branch(merge_block)

        self.generator.set_block(else_block)
        self.visit(block.false_branch)
        self.generator.branch(merge_block)

        self.generator.set_block(merge_block)

    def visit_WhileBlock(self, block):
        test_block = self.generator.add_block("whiletest")

        self.generator.branch(test_block)
        self.generator.set_block(test_block)

        self.generator.generate_code(block)

        loop_block = self.generator.add_block("loop")
        after_loop = self.generator.add_block("afterloop")

        self.generator.cbranch(block.testvar, loop_block, after_loop)

        self.generator.set_block(loop_block)
        self.visit(block.loop_branch)
        self.generator.branch(test_block)

        self.generator.set_block(after_loop)


class GenerateLLVM(object):
    def __init__(self):
        self.module = Module.new("module")
        self.builder = None
        self.exit_block = None
        self.functions = {}
        self.function = None
        self.last_branch = None
        self.block = None
        self.temps = {}
        self.locals = {}
        self.globals = {}
        self.vars = ChainMap(self.locals, self.globals)

    def declare_runtime_library(self):
        self.runtime = {}

        self.runtime['_print_int'] = Function.new(self.module,
                                                  Type.function(Type.void(), [int_type], False),
                                                  "_print_int")
        self.runtime['_print_float'] = Function.new(self.module,
                                                    Type.function(Type.void(), [float_type], False),
                                                    "_print_float")
        self.runtime['_print_bool'] = Function.new(self.module,
                                                   Type.function(Type.void(), [bool_type], False),
                                                   "_print_bool")

    def set_block(self, block):
        self.block = block
        self.builder.position_at_end(block)

    def add_block(self, name):
        return self.function.append_basic_block(name)

    def make_function(self, name, ret_type, arg_types):
        func = Function.new(self.module, Type.function(ret_type, arg_types, False), name)
        self.functions[name] = func
        self.globals[name] = func
        return func

    def terminate(self):
        if self.last_branch != self.block:
            self.builder.branch(self.exit_block)
        self.builder.position_at_end(self.exit_block)
        if 'return' in self.locals:
            self.builder.ret(self.builder.load(self.locals['return']))
        else:
            self.builder.ret_void()

    def begin_function(self, name, ret_type, arg_types):
        ret_type, arg_types = typemap[ret_type], [typemap[a] for a in arg_types]
        self.locals.clear()
        self.function = self.functions[name]
        self.block = self.function.append_basic_block("start")
        self.builder = Builder.new(self.block)
        self.set_block(self.block)
        self.exit_block = self.function.append_basic_block("exit")
        if ret_type is not void_type:
            self.locals['return'] = self.builder.alloca(ret_type, name="return")

    def end_function(self, name):
        if name == "@main":
            self.main_func = self.function
            self.branch(self.exit_block)
        self.terminate()
        if args.verbose:
            print("==== IN-PROGRESS MODULE ===")
            print(self.module)
            print("==== END IN-PROGRESS MODULE ===")
        if args.validate:
            self.function.verify()

    def cbranch(self, testvar, true_block, false_block):
        self.builder.cbranch(self.temps[testvar], true_block, false_block)

    def branch(self, next_block):
        if self.last_branch != self.block:
            self.builder.branch(next_block)
        self.last_branch = self.block

    def generate_code(self, block):
        for op in block.instructions:
            opcode = op[0]
            if hasattr(self, "emit_" + opcode):
                getattr(self, "emit_" + opcode)(*op[1:])
            elif args.verbose:
                print("Warning: No emit_" + opcode + "() method")

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_literal_int(self, value, target):
        self.temps[target] = Constant.int(int_type, value)

    def emit_literal_float(self, value, target):
        self.temps[target] = Constant.real(float_type, value)

    def emit_literal_bool(self, value, target):
        self.temps[target] = Constant.int(bool_type, 1 if value else 0)

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_global_int(self, name):
        var = GlobalVariable.new(self.module, int_type, name)
        var.initializer = Constant.int(int_type, 0)
        self.globals[name] = var

    def emit_global_float(self, name):
        var = GlobalVariable.new(self.module, float_type, name)
        var.initializer = Constant.real(float_type, 0.0)
        self.globals[name] = var

    def emit_global_bool(self, name):
        var = GlobalVariable.new(self.module, bool_type, name)
        var.initializer = Constant.int(bool_type, 0)
        self.globals[name] = var

    def emit_alloc_int(self, name):
        var = self.builder.alloca(int_type, name=name)
        self.locals[name] = var

    def emit_alloc_float(self, name):
        var = self.builder.alloca(float_type, name=name)
        self.locals[name] = var

    def emit_alloc_bool(self, name):
        var = self.builder.alloca(bool_type, name=name)
        self.locals[name] = var

    def emit_parm_int(self, name, argn):
        self.emit_alloc_int(name)
        self.builder.store(self.function.args[argn], self.vars[name])

    def emit_parm_float(self, name, argn):
        self.emit_alloc_float(name)
        self.builder.store(self.function.args[argn], self.vars[name])

    def emit_parm_bool(self, name, argn):
        self.emit_alloc_bool(name)
        self.builder.store(self.function.args[argn], self.vars[name])

    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_load_int(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_float(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_bool(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_store_int(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_float(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_bool(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_return_int(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_float(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_bool(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

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

    def emit_lt_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_SLT, self.temps[left], self.temps[right], target)

    def emit_gt_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_SGT, self.temps[left], self.temps[right], target)

    def emit_lte_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_SLE, self.temps[left], self.temps[right], target)

    def emit_gte_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_SGE, self.temps[left], self.temps[right], target)

    def emit_eq_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_EQ, self.temps[left], self.temps[right], target)

    def emit_neq_int(self, left, right, target):
        self.temps[target] = self.builder.icmp(ICMP_NE, self.temps[left], self.temps[right], target)

    def emit_lt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_ULT, self.temps[left], self.temps[right], target)

    def emit_gt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_UGT, self.temps[left], self.temps[right], target)

    def emit_lte_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_ULE, self.temps[left], self.temps[right], target)

    def emit_gte_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_UGE, self.temps[left], self.temps[right], target)

    def emit_eq_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_UEQ, self.temps[left], self.temps[right], target)

    def emit_neq_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp(FCMP_UNE, self.temps[left], self.temps[right], target)

    def emit_and_bool(self, left, right, target):
        self.temps[target] = self.builder.and_(self.temps[left], self.temps[right], target)

    def emit_or_bool(self, left, right, target):
        self.temps[target] = self.builder.or_(self.temps[left], self.temps[right], target)

    def emit_not_bool(self, source, target):
        self.temps[target] = self.builder.not_(self.temps[source])

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

    def emit_print_bool(self, source):
        self.builder.call(self.runtime['_print_bool'], [self.temps[source]])

    # Extern function declaration.
    def emit_extern_func(self, name, rettypename, *parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = Type.function(rettype, parmtypes, False)
        self.globals[name] = Function.new(self.module, func_type, name)

    # Call an external function.
    def emit_call_func(self, funcname, target, *funcargs):
        resolved_args = []
        for arg in funcargs:
            resolved_args.append(self.temps[arg])
        self.temps[target] = self.builder.call(self.vars[funcname], resolved_args)


def main():
    import gonelex
    import goneparse
    import gonecheck
    import gonecode
    import sys
    import ctypes
    import time
    import argparse
    from errors import subscribe_errors, errors_reported
    from llvm.ee import ExecutionEngine

    global args
    parser = argparse.ArgumentParser("Compile and run a Gone program from a .g file")
    parser.add_argument('file', type=str, default='', nargs=1,
                        help="the file containing Gone source")
    parser.add_argument('--verbose', '-v', action="store_true",
                        help="print verbose output")
    parser.add_argument('--validate', '-c', action="store_true",
                        help="perform llvm bitcode validation prior to program execution")
    args = parser.parse_args()

    # Load the Gone runtime library (see Makefile)
    ctypes._dlopen('./gonert.so', ctypes.RTLD_GLOBAL)

    lexer = gonelex.make_lexer()
    parser = goneparse.make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse(open(args.file[0]).read())
        gonecheck.check_program(program)
        if not errors_reported():
            code = gonecode.generate_code(program)
            g = GenerateLLVMBlockVisitor()
            g.visit_functions(code.functions)

            if args.verbose:
                print("---- NATIVE ASSEMBLY ----")
                print(g.generator.module.to_native_assembly())
                print("---- END NATIVE ASSEMBLY ----")

            if args.verbose:
                print(":::: RUNNING ::::")
            start = time.time()

            llvm_executor = ExecutionEngine.new(g.generator.module)
            llvm_executor.run_function(g.generator.main_func, [])

            if args.verbose:
                print(":::: FINISHED ::::")
                print("execution time: {0:.15f}s".format(time.time() - start))

if __name__ == '__main__':
    main()
