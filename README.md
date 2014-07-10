"Gone" Compiler
===============

This is a compiler for a tiny programming language called "Gone", implemented
using python, PLY, and llvmpy. "Gone" is a small subset of Go with support for
basic imperative programming language features.

Use
---

    python goner.py tests/llvm/good.g

Files
-----

* `goneast.py`: models of AST nodes representing pieces of a Gone program
* `gonecheck.py`: an AST visitor that performs type-checking on a Gone AST
* `gonecode.py`: an AST visitor that generates intermediate SSA code from a Gone AST
* `goneinterp.py`: an interpreter for Gone SSA instructions
* `gonelex.py`: a lexer for tokens in the Gone language
* `gonellvm.py`: generates llvm "bitcode" from Gone SSA instructions
* `goneparse.py`: a parser generator for Gone, defining the grammar
* `goner.py`: the main entry point to the compiler
* `gonert.c`: the C implementation of system-level calls for the Gone runtime (such as printing)
* `gonetype.py`: definitions of the datatypes Gone supports

You can run most of these python files on any of the files in the `tests`
directory to view the intermediate stages of lexing, parsing, type checking,
code generation, and running.
