from parser import parse
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

if __name__ == '__main__':
    """Parse Nouva code from the CLI"""

    code = sys.argv[1]
    ast = parse(code)
    debug_print_ast(ast)
