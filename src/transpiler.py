from parser import parse

def transpile_part(item):
    # basic checks
    if item == None:
        return 'undefined'
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
                case '=!': js_operation = '=!' + ident
            return f"{ident} {js_operation}"
        case 'return_statement':
            value = collect("value")
            return f"return {value};"
        
        # atomics:
        case 'identifier':
            return item["Name"]
        case 'number':
            return item["Value"]
        
        # default
        case _: return f'/* error {item} */'

def transpile(code):
    """Transpile a Nouva code string to JavaScript"""
    parse_tree = parse(code)
    js = ''
    for item in parse_tree["body"]:
        js += transpile_part(item)
    return js
