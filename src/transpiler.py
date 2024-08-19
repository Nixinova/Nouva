from parser import parse

use_compiler = False
declared_vars = []
errors = []

_UNIQDELIM = "ab467d4984e596ba" # arbitrary ID used to delimit intermediate transpilations that require reparsing in a parent token
def intermediary_pack(values):
    return _UNIQDELIM.join(values)
def intermediary_unpack(str):
    return str.split(_UNIQDELIM)

def transpile_part(item):
    # quick exceptions for fundamental JS types
    if item == None:
        return 'undefined'
    if item == True or item == False:
        return str(item).lower()
    # basic type checks
    if isinstance(item, str):
        return item
    if isinstance(item, list):
        js = ''
        for subitem in item:
            js += transpile_part(subitem)
        return js
    
    def collect(key):
        return transpile_part(item[key])

    # parse token
    """Note: naming format of keys:
        - Constants: UPPERCASE
        - Collated strings: Capitalised
        - Subtokens: lowercase
       Ensure sync with parser.py
    """
    match item["TOKEN"]:
        
        # blocks of code
        case 'function_decl':
            ident = collect("identifier")
            params = item["parameters"]
            js_param_list = ','.join(params)
            body = collect("body")
            
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
            
            return f"function {ident}({js_param_list}) {'{'}\n{body}{'}'}\n" 
        case 'class_decl':
            ident = collect("identifier")
            body = collect("body")
            
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
            
            return f"class {ident} {'{'}\n{body}{'}'}\n"
        
        # line of code
        case 'statement':
            return collect("body") + ';\n'
        case 'declaration':
            varword = collect("varword")
            ident = collect("identifier")
            [value, type_val] = intermediary_unpack(collect("body")) # NOTE: collects from packed intermediary result
            js_varword = ''
            match varword:
                case 'var': js_varword = 'let'
                case 'val': js_varword = 'const'
                
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
                
            return f"{js_varword} {ident} /*/: {type_val}/*/ = {value}"
        # NOTE: returns packed intermediary result (must be unpacked)
        case 'declaration_body':
            value = collect("value")
            type_idents = []
            for type_item in item["type"]:
                type_idents.append(transpile_part(type_item))
            type_val = '|'.join(type_idents)
            return intermediary_pack([value, type_val])
        case 'definition':
            ident = collect("identifier")
            value = collect("value")
            
            if use_compiler:
                if not ident in declared_vars:
                    raise Exception(f"CompileError: ident {ident} is not defined")
            
            return f"{ident} = {value}"
        case 'reassignment':
            ident = collect("identifier")
            operator = collect("operator")
            value = collect("value")
            
            if use_compiler:
                if not ident in declared_vars:
                    raise Exception(f"CompileError: ident {ident} is not defined")
            
            return f"{ident} {operator} {value}"
        case 'unary_reassignment':
            ident = collect("identifier")
            operator = collect("operator")
            js_operation = ''
            match operator:
                case '=!=': js_operation = '=!' + ident
                
            if use_compiler:
                if not ident in declared_vars:
                    raise Exception(f"CompileError: ident {ident} is not defined")
            
            return f"{ident} {js_operation}"

        case 'return_statement':
            value = collect("value")
            return f"return {value};\n"
        
        # expressions
        case 'method_call':
            ident = collect("identifier")
            key = item["Key"]
            args = collect("arguments")
            return f"{ident}.{key}({args})"
        
        case 'unary_expression':
            op = item["Operator"]
            rhs = transpile_part(item["rhs"])
            return f"{op} {rhs}"
        case 'math_expression' | 'bitwise_expression' | 'logical_expression' | 'comparison_expression':
            lhs = transpile_part(item["lhs"])
            op = item["Operator"]
            rhs = transpile_part(item["rhs"])
            # Nouva->JS conversions
            if op == '^': op = '**'
            elif op == '^=': op = '**='
            elif op == '><': op = '^'
            elif op == '><=': op = '^='
            
            return f"{lhs} {op} {rhs}"
        
        case 'lambda_expression':
            params = item["parameters"]
            js_param_list = ','.join(params)
            body = collect("body")
            return f"({js_param_list}) => {body}"
        
        # atomics:
        case 'identifier':
            ident = item["Name"]
            js_ident = ident.replace('#', '_').replace('?', '')
            return js_ident
        case 'number':
            return transpile_part(item["value"])
        case 'based_number':
            base = int(item["Base"])
            num = item["Value"]
            if base == 2: return '0b' + num
            if base == 8: return '0o' + num
            if base == 16: return '0x' + num
            # for any other base:
            try:
                return int(num, base)
            except:
                # final fallback
                # TODO support decimals of arbitrary bases
                return f"parseInt('{num}', {base})"
        
        # default
        case _: return f'/* error {item} */'

def run_transpiler(code):
    """Transpile a Nouva code string to JavaScript"""
    parse_tree = parse(code)
    
    global declared_vars
    declared_vars = []
    
    js = ''
    for item in parse_tree["body"]:
        js += transpile_part(item)
    return js

def transpile(code):
    global use_compiler
    use_compiler = False
    
    return run_transpiler(code)

def compile(code):
    global use_compiler
    use_compiler = True
    
    return run_transpiler(code)
