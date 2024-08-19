from parser import parse
from transpiler import transpile, compile
import sys

def debug_print_ast(node, indent=0):
    """Recursively print contents of the AST tree."""
    if isinstance(node, dict):
        for key, value in node.items():
            print(' ' * indent + f"{key}:")
            debug_print_ast(value, indent + 2)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            print(' ' * indent + f"[{i}]")
            debug_print_ast(item, indent + 2)
    else:
        print(' ' * indent + str(node))

def cli():
    """Parse Nouva code from the CLI"""

    [_, func, code, *args] = sys.argv
    if func == 'parse':
        ast = parse(code)
        debug_print_ast(ast)
    elif func == 'transpile':
        js_code = transpile(code)
        print(js_code)
    elif func == 'compile':
        if len(args) > 0:
            js_code = compile(code, args[0])
            print(js_code)
        else:
            print("ERROR: Please input a valid language at the end of your query string! Options: JS, TS.")

if __name__ == '__main__': cli()
