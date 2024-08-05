# Nouva

The **Nouva** programming language.

Explore the syntax of Nouva in **[syntax.md](syntax.md)**.

This language uses a Lark grammar: **[grammar.lark](src/grammar.lark)**.
Use a Lark compiler such as [lark-parser.org](https://www.lark-parser.org/ide/) to preview the Nouva grammar.

Parse Nouva code using **[parser.py](src/parser.py)**.
Run it from the CLI using [cli.py](src/cli.py): `python src/cli.py parse "var x = true;"`.

Transpile Nouva code to JavaScript using **[transpiler.py](src/transpiler.py)**.
Run it from the CLI using cli.py also: `python src/cli.py transpile "var x = true;"`.
