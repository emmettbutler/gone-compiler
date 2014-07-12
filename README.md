"Gone" Compiler
===============

This is a compiler for a tiny programming language called "Gone", implemented
using python, PLY, and llvmpy. "Gone" is a small subset of Go with support for
basic imperative programming language features.

This compiler was developed under the supervision of David Beazley (@dabeaz)
during a week-long course in July 2014.

Use
---

    make ; make linux
    python3 goner.py tests/functions/mandel.g

Files
-----

* `goneast.py`: models of AST nodes representing pieces of a Gone program
* `goneblock.py`: models of blocks used during code generation
* `gonecheck.py`: an AST visitor that performs type-checking on a Gone AST
* `gonecode.py`: an AST visitor that generates intermediate SSA code from a Gone AST
* `goneinterp.py`: an interpreter for some Gone SSA instructions (partially implemented)
* `gonelex.py`: a lexer for tokens in the Gone language
* `gonellvm.py`: generates llvm "bitcode" from Gone SSA instructions
* `goneparse.py`: a parser generator for Gone, defining the grammar
* `goner.py`: the main entry point to the compiler
* `gonert.c`: the C implementation of system-level calls for the Gone runtime (such as printing)
* `gonetype.py`: definitions of the datatypes Gone supports

You can run most of these python files on any of the files in the `tests`
directory to view the intermediate stages of lexing, parsing, type checking,
code generation, and running.

Requirements
------------

This compiler is written in python3, so you'll need that. It also depends on
[ply](http://www.dabeaz.com/ply/), which you can get with

    `pip install -r requirements.txt`

This compiler targets [llvm](http://llvm.org/releases/download.html)
and uses [llvmpy](http://www.llvmpy.org/llvmpy-doc/dev/doc/firstexample.html),
so you'll need to install both to use it. It's been tested with llvm 3.3. The
easiest way to get llvmpy is to install it using
[Anaconda](http://continuum.io/downloads).

You can also use `goneinterp.py` to run programs that don't include
conditionals, loops, or user-defined functions, as the interpreter does not
support these features.
