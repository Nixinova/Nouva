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
            jsvarword = 'let' if varword == 'var' else 'const'
            ident = collect("identifier")
            body = collect("body")
            return f"{jsvarword} {ident} = {body};"
        case 'declaration_body':
            value = collect("value") or 'undefined'
            return value
        case 'definition':
            ident = collect("identifier")
            value = collect("value")
            return f"{ident} = {value};"
        
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
