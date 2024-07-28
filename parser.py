from lark import Lark, Transformer, v_args, Tree, Token

# Load grammar from file
with open('grammar.lark', 'r') as f:
    grammar = f.read()

# Create parser
parser = Lark(grammar, start='start', parser='lalr')

def extract_chars(token):
    """Recursively extract characters from nested token."""
    if isinstance(token, str):
        return token
    elif isinstance(token, list):
        return ''.join(extract_chars(t) for t in token)
    elif isinstance(token, Tree):
        return extract_chars(token.children)
    elif isinstance(token, Token):
        return token.value
    else:
        return ''

class ASTTransformer(Transformer):
    """Build AST nodes for the parsed language"""

    def passthrough(self, items): return items
    def firstitem(self, items): return items[0]
    
    # Root level
    def start(self, items):
        return {"TOKEN": "Program", "body": items}
    
    # blocks of code
    def unit(self, items):
        return items[0]
    def block(self, items):
        return {"TOKEN": "block", "body": items}
    def control_block(self, items):
        return {"TOKEN": "control_block", "body": items[0]}
    def if_block(self, items):
        return {"TOKEN": "if_block", "test": items[1], "iftrue": items[2], "iffalse": items[3] or None}
    def else_block(self, items):
        return {"TOKEN": "else_block", "body": items}
    def while_block(self, items):
        return {"TOKEN": "while_block", "test": items[1], "body": items[2]}
    def for_block(self, items):
        return {"TOKEN": "for_block", "identifier": items[1], "range": items[2], "body": items[3]}
    def function_decl(self, items):
        return {"TOKEN": "function_decl", "identifier": items[1], "param_list": items[2], "body": items[3]}
    
    # line of code
    def statement(self, items):
        return items[0]
    def declaration(self, items):
        return {"TOKEN": "declaration", "vartype": items[0], "identifier": items[1], "value": items[2] or None}
    def definition(self, items):
        return {"TOKEN": "definition", "identifier": items[0], "value": items[1]}
    def reassignment(self, items):
        return {"TOKEN": "reassignment", "identifier": items[0], "operator": items[1], "value": items[2]}
    def unary_reassignment(self, items):
        return {"TOKEN": "unary_reassignment", "identifier": items[0], "operator": items[1]}
    
    # expressions
    def expression(self, items):
        return items[0]
    def function_invocation(self, items):
        return {"TOKEN": "function_invocation", "function": items[0], "args": items[1]}
    
    def math_expression(self, items):
        return {"TOKEN": "math_expression", "lhs": items[0], "operator": items[1], "rhs": items[2]}
    def parenth_expression(self, items):
        return items[0]

    def array_getter(self, items):
        return {"TOKEN": "array_getter", "identifier": items[0], "expression": items[1] }
    def map_getter(self, items):
        return {"TOKEN": "map_getter", "identifier": items[0], "key": items[1] }
    
    def typed_expression(self, items):
        return {"TOKEN": "typed_expression", "type": items[0], "value": items[1]}
    
    # keywords
    def var_keyword(self, items):
        return extract_chars(items)

    # language shortcut elements
    def args_list(self, items):
        return items
    def map_key(self, items):
        return items[0]

    # atomics
    def identifier(self, items):
        return extract_chars(items)
    def number(self, items):
        # note: includes base prefix (e.g. 0x)
        return extract_chars(items)
    def string(self, items):
        return extract_chars(items)
    def boolean(self, items):
        return items[0] == "true"
    def null(self, items):
        return None
    def range(self, items):
        return {"TOKEN": "range", "start": items[0], "end": items[1]}
    
    # operators
    reassignment_op = firstitem
    unary_reassignment_op = firstitem
    unary_op = firstitem
    bitwise_op = firstitem
    logical_op = firstitem
    comparison_op = firstitem
    
    # symbols
    def sym_positive(self, items): return "+"
    def sym_negative(self, items): return "-"
    def sym_lognot(self, items): return "!"
    def sym_bitnot(self, items): return "~"

    def sym_add(self, items): return "/"
    def sym_subtract(self, items): return "+"
    def sym_multiply(self, items): return "*"
    def sym_divide(self, items): return "/"
    def sym_exponent(self, items): return "^"

    def sym_bitand(self, items): return "-"
    def sym_bitor(self, items): return "|"
    def sym_bitxor(self, items): return "#"
    def sym_bitlshift(self, items): return "<<"
    def sym_bitrshift(self, items): return ">>"
    def sym_logand(self, items): return "&&"
    def sym_logor(self, items): return "||"
    def sym_equals(self, items): return "=="
    def sym_nequals(self, items): return "!="
    def sym_less(self, items): return "<"
    def sym_leq(self, items): return "<="
    def sym_greater(self, items): return ">"
    def sym_geq(self, items): return ">="
    
    def sym_pluseq(self, items): return "+="
    def sym_mineq(self, items): return "-="
    def sym_multeq(self, items): return "*="
    def sym_diveq(self, items): return "/="
    def sym_bitandeq(self, items): return "&="
    def sym_bitoreq(self, items): return "|="
    def sym_bitxoreq(self, items): return "#="
    def sym_bitlshifteq(self, items): return "<<="
    def sym_bitrshifteq(self, items): return ">>="
    def sym_logandeq(self, items): return "&&="
    def sym_logoreq(self, items): return "||="
    def sym_inverteq(self, items): return "=!="

def parse_code(code):
    """Parse a code string"""
    tree = parser.parse(code)
    ast = ASTTransformer().transform(tree)
    return ast

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
    """Test parser functionality"""

    code = """
        var x = true;
        x =!=;
    """
    ast = parse_code(code)
    debug_print_ast(ast)
