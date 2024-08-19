import re
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
            params = []
            for param_item in item["parameters"]:
                params.append(transpile_part(param_item))
            param_list = ','.join(params)
            body = collect("body")
            
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
            
            return f"function {ident}({param_list}) {'{'}\n{body}{'}'}\n" 
        case 'class_decl':
            ident = collect("identifier")
            params = []
            param_idents = []
            for param_item in item["parameters"]:
                params.append(transpile_part(param_item))
                param_idents.append(param_item["Identifier"])
            body = collect("body")
            
            # create constructor
            constructor_body = ''
            for param in param_idents:
                constructor_body += f"this.{param} = {param};\n"
            full_body = f"constructor({','.join(params)}) {'{'} {constructor_body} {'}'}\n" + body
            
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
            
            return f"class {ident} {'{'}\n{full_body}{'}'}\n"
        
        # line of code
        case 'statement':
            return collect("body") + ';\n'
        case 'declaration':
            var_keyword = collect("varword")
            ident = collect("identifier")
            [value, type_val] = intermediary_unpack(collect("body")) # NOTE: collects from packed intermediary result
            varword = ''
            match var_keyword:
                case 'var': varword = '/*ES/let/*/'
                case 'val': varword = '/*ES/const/*/'
                
            if use_compiler:
                if ident in declared_vars:
                    raise f"CompileError: ident {ident} already exists"
                declared_vars.append(ident)
                
            return f"{varword} {ident} {type_val and f"/*TS/: {type_val}/*/" or ''} = {value}"
        # NOTE: returns packed intermediary result (must be unpacked)
        case 'declaration_body':
            value = collect("value")
            types = item["type"]
            type_idents = []
            for type_item in types or []:
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
        
        case 'throw_statement':
            body = collect("body")
            return f"throw {body}"

        case 'return_statement':
            value = collect("value")
            return f"return {value};\n"
        
        # expressions
        case 'function_invocation':
            name = collect("function").replace('!', '').replace('?', '').replace('#', '')
            args = collect("args")
            handler = item["handler"] and collect("handler")
            if handler:
                return f"(function() {'{'}\ntry {'{'}\nreturn {name}({args});\n{'}'} catch(_e$) {'{'}\n({handler})(_e$);\n{'}'}\n{'}'})()"
            else:
                return f"{name}({args})"
        case 'catcher':
            ident = collect("identifier")
            body = collect("body")
            return f"(function({ident}) {'{'}\n{body}\n{'}'})"
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
            params = []
            for param_item in item["parameters"]:
                params.append(transpile_part(param_item))
            param_list = ','.join(params)
            body = collect("body")
            return f"({param_list}) => {body}"
        
        # basic elements:
        case 'function_param':
            ident = item["Identifier"]
            type_union = '|'.join(item["Type"])
            return f"{ident} /*TS/: {type_union}/*/"
        
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

def compile(code, lang):
    global use_compiler
    use_compiler = True
    
    result = run_transpiler(code)
    
    match lang.lower():
        case 'js':
            # output JS-only or ES features
            result = re.sub(r"\/\*(?:JS|ES)\/(.+?)\/\*\/", r'\1', result)
        case 'ts':
            # output TS-only or ES features
            result = re.sub(r"\/\*(?:TS|ES)\/(.+?)\/\*\/", r'\1', result)
    result = re.sub(r"\/\*.+?\/\*\/", '', result)
    
    return result
