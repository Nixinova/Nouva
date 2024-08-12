from parser import parse

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
        # line of code
        case 'declaration':
            varword = collect("varword")
            ident = collect("identifier")
            body = collect("body")
            js_varword = ''
            match varword:
                case 'var': js_varword = 'let'
                case 'val': js_varword = 'const'
            return f"{js_varword} {ident} = {body}"
        case 'declaration_body':
            value = collect("value") or 'undefined'
            return value
        case 'definition':
            ident = collect("identifier")
            value = collect("value")
            return f"{ident} = {value};"
        case 'reassignment':
            ident = collect("identifier")
            operator = collect("operator")
            value = collect("value")
            return f"{ident} {operator} {value}"
        case 'unary_reassignment':
            ident = collect("identifier")
            operator = collect("operator")
            js_operation = ''
            match operator:
                case '=!=': js_operation = '=!' + ident
            return f"{ident} {js_operation}"
        case 'return_statement':
            value = collect("value")
            return f"return {value};"
        
        # expressions
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
        
        # atomics:
        case 'identifier':
            return item["Name"]
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

def transpile(code):
    """Transpile a Nouva code string to JavaScript"""
    parse_tree = parse(code)
    js = ''
    for item in parse_tree["body"]:
        js += transpile_part(item)
    return js
