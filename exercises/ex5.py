from llvm.core import Module, Builder, Function, Type, Constant, GlobalVariable
from llvm.ee import ExecutionEngine, GenericValue
import ctypes

mod = Module.new("hello")
hello_func = Function.new(mod, Type.function(Type.int(), [], False), "hello")
block = hello_func.append_basic_block('entry')
builder = Builder.new(block)
builder.ret(Constant.int(Type.int(), 69))
#print(mod)

engine = ExecutionEngine.new(mod)
result = engine.run_function(hello_func, [])
#print(result.as_int())


dsquared_func = Function.new(mod, Type.function(Type.double(), [Type.double(),
                             Type.double()], False), "dsquared")
block = dsquared_func.append_basic_block("entry")
builder = Builder.new(block)

x = dsquared_func.args[0]
xsquared = builder.fmul(x, x)
y = dsquared_func.args[1]
ysquared = builder.fmul(y, y)

d2 = builder.fadd(xsquared, ysquared)
builder.ret(d2)
#print(mod)

a = GenericValue.real(Type.double(), 3.0)
b = GenericValue.real(Type.double(), 4.0)
result = engine.run_function(dsquared_func, [a, b])
#print(result.as_real(Type.double()))


sqrt_func = Function.new(mod, Type.function(Type.double(), [Type.double()], False), "sqrt")
r = engine.run_function(sqrt_func, [result])
#print(r.as_real(Type.double()))

# define a function that calls a function
distance_func = Function.new(mod, Type.function(Type.double(),
                             [Type.double(), Type.double()], False), "distance")
block = distance_func.append_basic_block("entry")
builder = Builder.new(block)
x = distance_func.args[0]
y = distance_func.args[1]
d2 = builder.call(dsquared_func, [x,y])
d = builder.call(sqrt_func, [d2])
builder.ret(d)

result = engine.run_function(distance_func, [a, b])
#print(result.as_real(Type.double()))

# run a function from a dynamically loaded c library
ctypes._dlopen("./rtlib.so", ctypes.RTLD_GLOBAL)
print_float_func = Function.new(mod, Type.function(Type.void(),
                                [Type.double()], False), "print_float")
engine.run_function(print_float_func, [result])


main_func = Function.new(mod, Type.function(Type.void(), [], False), "main")
block = main_func.append_basic_block("entry")
builder = Builder.new(block)
x = Constant.real(Type.double(), 3.0)
y = Constant.real(Type.double(), 4.0)
d = builder.call(distance_func, [x,y])
builder.call(print_float_func, [d])
builder.ret_void()
engine.run_function(main_func, [])

x_var = GlobalVariable.new(mod, Type.double(), "x")
x_var.initializer = Constant.real(Type.double(), 0.0)

incr_func = Function.new(mod, Type.function(Type.void(), [], False), "incr")
block = incr_func.append_basic_block("entry")
builder = Builder.new(block)
tmp1 = builder.load(x_var)
tmp2 = builder.fadd(tmp1, Constant.real(Type.double(),1.0))
builder.call(print_float_func, [tmp2])
builder.store(tmp2, x_var)
builder.ret_void()
print(mod)

for i in range(10):
    r = engine.run_function(incr_func, [])
