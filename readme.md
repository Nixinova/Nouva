# Nouva

The **Nouva** programming language.

Explore the syntax of Nouva in **[syntax.md](syntax.md)**.

This language uses a Lark grammar: **[grammar.lark](src/grammar.lark)**.
Use a Lark compiler such as [lark-parser.org](https://www.lark-parser.org/ide/) to preview the Nouva grammar.

Parse Nouva code using **[parser.py](src/parser.py)**.
Try it from the CLI: `bin/parse "var x = true;"`.

Transpile Nouva code to JavaScript using **[transpiler.py](src/transpiler.py)**.
Try it from the CLI: `bin/transpile "var x = true;"`.

Basic compilation is also available, which does the above transpilation but with error reporting.
Try it from the CLI: `bin/compile "var x = true;"`.
