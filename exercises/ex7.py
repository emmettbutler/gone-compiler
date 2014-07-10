def foo(a, b):
    if a < b:
        print("yes")
    else:
        print("no")

import dis


def countdown(n):
    while n > 0:
        print("T-minus", n)
        n -= 1

code = """\
start
if a < 0:
    a + b
else:
    a - b
done
"""

import ast
top = ast.parse(code)
