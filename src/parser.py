import os

from lark import Lark, Transformer, Tree, Token

dir_path = os.path.dirname(os.path.realpath(__file__))
GRAMMAR_FILE = dir_path + "/grammar.lark"

# Load grammar from file
with open(GRAMMAR_FILE, 'r') as f:
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
    
    """Naming guideliness for keys:
        - Constants: UPPERCASE
        - Collated strings: Capitalised
        - Subtokens: lowercase
       Ensure sync with transpiler.py
    """

    def passthrough(self, items): return items
    def firstitem(self, items): return items[0]
    
    # Root level
    def start(self, items):
        return {"TOKEN": "Program", "body": items}
    
    # fundamentals
    def imports(self, items):
        return {"TOKEN": "imports", "body": items}
    def unit(self, items):
        return items[0]
    
    # blocks of code
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
    def switch_block(self, items):
        return {"TOKEN": "switch_block", "expression": items[1], "body": items[2]}

    switch_body = passthrough
    def switch_case(self, items):
        return {"TOKEN": "switch_case", "cases": items[1], "body": items[2]}
    def switch_default(self, items):
        return {"TOKEN": "switch_default", "body": items[1]}
    
    def function_decl(self, items):
        return {"TOKEN": "function_decl", "identifier": items[1], "param_list": items[2], "body": items[3]}
    func_block = passthrough
    
    def class_decl(self, items):
        return {"TOKEN": "class_decl", "identifier": items[1], "body": items[2]}
    class_body = passthrough
    def constructor(self, items):
        return {"TOKEN": "constructor", "params": items[0], "body": items[1]}
    def method(self, items):
        return {"TOKEN": "method", "identifier": items[1], "params": items[2], "body": items[3]}
    
    # line of code
    def module_statement(self, items):
        return {"TOKEN": "module_statement", "path": items[1]}
    def import_statement(self, items):
        return {"TOKEN": "import_statement", "path": items[1]}

    def statement(self, items):
        return items[0]
    
    def declaration(self, items):
        return {"TOKEN": "declaration", "varword": items[0], "identifier": items[1], "body": items[2] or None}
    declaration_contents = passthrough
    def typed_decl(self, items):
        return {"TOKEN": "declaration_body", "type": items[0], "value": None}
    def valued_decl(self, items):
        return {"TOKEN": "declaration_body", "type": None, "value": items[0]}
    def typed_valued_decl(self, items):
        return {"TOKEN": "declaration_body", "type": items[0], "value": items[1]}
    
    def definition(self, items):
        return {"TOKEN": "definition", "identifier": items[0], "value": items[1]}
    def reassignment(self, items):
        return {"TOKEN": "reassignment", "identifier": items[0], "operator": items[1], "value": items[2]}
    def unary_reassignment(self, items):
        return {"TOKEN": "unary_reassignment", "identifier": items[0], "operator": items[1]}
    def return_statement(self, items):
        return {"TOKEN": "return_statement", "value": items[1]}
    
    # expressions
    expression_list = passthrough
    
    def expression(self, items):
        return items[0]
    
    definition_expression = passthrough
    
    def function_invocation(self, items):
        return {"TOKEN": "function_invocation", "function": items[0], "args": items[1]}
    def array_getter(self, items):
        return {"TOKEN": "array_getter", "identifier": items[0], "expression": items[1] }
    def map_getter(self, items):
        if items[2] == None:
            return {"TOKEN": "map_getter", "identifier": items[0], "key": items[1] }
        else:
            return {"TOKEN": "method_call", "identifier": items[0], "key": items[1], "arguments": items[2] }
            
    def typed_expression(self, items):
        return {"TOKEN": "typed_expression", "type": items[0], "value": items[1]}
    def unary_expression(self, items):
        return {"TOKEN": "unary_expression", "Operator": items[0], "rhs": items[1]}
    def math_expression(self, items):
        return {"TOKEN": "math_expression", "lhs": items[0], "Operator": items[1], "rhs": items[2]}
    def bitwise_expression(self, items):
        return {"TOKEN": "bitwise_expression", "lhs": items[0], "Operator": items[1], "rhs": items[2]}
    def logical_expression(self, items):
        return {"TOKEN": "logical_expression", "lhs": items[0], "Operator": items[1], "rhs": items[2]}
    def comparison_expression(self, items):
        return {"TOKEN": "comparison_expression", "lhs": items[0], "Operator": items[1], "rhs": items[2]}
    
    block_expression = passthrough
    def function_expression(self, items):
        return {"TOKEN": "function_expression", "params": items[1], "body": items[2]}
    def lambda_expression(self, items):
        return {"TOKEN": "lambda_expression", "params": items[1], "body": items[2]}
    
    def parenth_expression(self, items):
        return items[0]
    
    # keywords
    def var_keyword(self, items):
        return extract_chars(items)

    # language shortcut elements
    params_list = passthrough
    def args_list(self, items):
        return items
    def map_key(self, items):
        return items[0]
    
    # atomics
    def identifier(self, items):
        return {"TOKEN": "identifier", "Name": extract_chars(items)}
    variable_identifier = identifier

    def number(self, items):
        return {"TOKEN": "number", "value": items[0]}
    def based_number(self, items):
        [value, base] = items[0].split('_')
        return {"TOKEN": "based_number", "Base": base, "Value": value}
    def numeral(self, items):
        return extract_chars(items)
    digit = firstitem
    
    def string(self, items):
        return extract_chars(items)
    
    def boolean(self, items):
        return items[0] == "true"
    
    def null(self, items):
        return None
    
    def array(self, items):
        indices = [item for i, item in enumerate(items) if i % 2 == 0]
        values = [item for i, item in enumerate(items) if i % 2 == 1]
        return {"TOKEN": "array", "indices": indices, "values": values}
    
    def map(self, items):
        keys = [item for i, item in enumerate(items) if i % 2 == 0]
        values = [item for i, item in enumerate(items) if i % 2 == 1]
        return {"TOKEN": "map", "keys": keys, "values": values}
    
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
    def sym_add(self, items): return "+"
    def sym_subtract(self, items): return "-"
    def sym_multiply(self, items): return "*"
    def sym_divide(self, items): return "/"
    def sym_exponent(self, items): return "^"

    def sym_bitand(self, items): return "&"
    def sym_bitor(self, items): return "|"
    def sym_bitxor(self, items): return "><"
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
    def sym_expeq(self, items): return "^="
    def sym_bitandeq(self, items): return "&="
    def sym_bitoreq(self, items): return "|="
    def sym_bitxoreq(self, items): return "><="
    def sym_bitlshifteq(self, items): return "<<="
    def sym_bitrshifteq(self, items): return ">>="
    def sym_logandeq(self, items): return "&&="
    def sym_logoreq(self, items): return "||="
    def sym_inverteq(self, items): return "=!="
    
    def sym_private(self, items): return "#"
    def sym_nullable(self, item): return "?"

def parse(code):
    """Parse a code string"""
    tree = parser.parse(code)
    ast = ASTTransformer().transform(tree)
    return ast

def get_parser():
    return parser
