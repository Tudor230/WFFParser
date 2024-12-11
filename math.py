from collections import defaultdict
import ply.yacc as yacc
from lexer import tokens, user_defined_symbols, symbol_aliases
import re
from anytree import Node, RenderTree
static_precedence = [
    ('right', 'IMPLIES', 'IFF'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
]
combined_symbols = []
for function_name, details in user_defined_symbols["functions"].items():
    combined_symbols.append((function_name, details["type"], details["precedence"]))

for predicate_name, details in user_defined_symbols["predicates"].items():
    combined_symbols.append((predicate_name, details["type"], details["precedence"]))
combined_symbols_sorted = sorted(combined_symbols, key=lambda item: (item[2], item[1]))
grouped_precedence = defaultdict(list)
for name, symbol_type, precedence_level in combined_symbols_sorted:
    if symbol_type == "infix":
        grouped_precedence[(precedence_level, "left")].append(symbol_aliases[name] if name in symbol_aliases else name)
    elif symbol_type == "prefix":
        grouped_precedence[(precedence_level, "right")].append(symbol_aliases[name] if name in symbol_aliases else name)
precedence = []
for (precedence_level, assoc), names in sorted(grouped_precedence.items()):
    precedence.append((assoc, *names))
precedence = static_precedence + precedence + [('right', 'NEG', 'LMODULE'), ('left', 'RMODULE'), ('left', "HIGHPREC")]
precedence = tuple(precedence)

def is_predicate(expr):
    """Check if the given expression is a predicate."""
    return isinstance(expr, tuple) and expr[0] in user_defined_symbols['predicates']

def is_function(expr):
    """Check if the given expression is a function."""
    return isinstance(expr, tuple) and expr[0] in user_defined_symbols['functions']

def p_start(p):
    """start : expression"""
    p[0] = p[1]

def p_negation(p):
    """expression : NEG expression"""
    print(f"Detected negation: {p[1]} {p[2]}")
    if is_predicate(p[2]):
        raise Exception(f"Error: Function - cannot be applied to predicate: {p[2]}.")
    p[0] = (p[1], p[2])

def p_module_expression(p):
    """expression : LMODULE expression RMODULE"""
    print(f"Detected module expression: {p[1]} {p[2]} {p[3]}")
    p[0] = ('|', p[2])

def p_invisible_multiplication(p):
    """expression : NUMBER expression %prec HIGHPREC
                    | VARIABLE expression %prec HIGHPREC
                    | CONSTANT expression %prec HIGHPREC
                    | expression expression %prec HIGHPREC"""
    # """expression : expression expression"""
    print(f"Detected invisible multiplication between: {p[1]} {p[2]}")
    p[0] = ('□□', p[1], p[2])

def p_expression_base(p):
    """expression : VARIABLE
                  | CONSTANT
                  | NUMBER
                  | SET"""
    p[0] = p[1]
    print(f"Detected base expression: {p[1]}")

def p_expression_binary(p):
    """expression : expression AND expression
                  | expression OR expression
                  | expression IMPLIES expression
                  | expression IFF expression"""
    print(f"Detected binary expression: {p[1]} {p[2]} {p[3]}")
    if (is_predicate(p[1]) or p[1][0] in ["¬", "∧", "∨", "⇒", "⇔", "∀", "∃"]) and (is_predicate(p[3]) or p[3][0] in ["¬", "∧", "∨", "⇒", "⇔", "∀", "∃"]):
        p[0] = (p[2], p[1], p[3])
    else:
        raise Exception(f"Error: Binary logical operators can only be used between predicates.")

def p_expression_unary(p):
    """expression : NOT expression"""
    print(f"Detected unary expression: {p[1]} {p[2]}")
    if is_predicate(p[2]) or p[2][0] in ["¬", "∧", "∨", "⇒", "⇔", "∀", "∃"]:
        p[0] = (p[1], p[2])
    else:
        raise Exception(f"Error: Unary logical operator 'NOT' can only be used with predicates.")

def p_expression_quantifier(p):
    """expression : FORALL VARIABLE expression
                  | EXISTS VARIABLE expression
                  | NEXISTS VARIABLE expression
                  | UEXISTS VARIABLE expression
                  | FORALL expression expression
                  | EXISTS expression expression
                  | NEXISTS expression expression
                  | UEXISTS expression expression"""
    # Might need to add a check for parentheses
    print(f"Detected quantifier expression: {p[1]} {p[2]} {p[3]}")
    if is_predicate(p[2]):
        p[3] = ( "⇒" if p[1] == "∀" else "∧", p[2], p[3])
        temp=""
        for args in reversed(p[2][1]):
            if temp:
                temp = (p[1], args, temp)
            else:
                temp = (p[1], args, p[3])
        p[0] = temp
    elif p[2][0] == "∧":
        tuples = extract_membership(p[2])
        temp=""
        for tup in reversed(tuples):
            p[3] = ( "⇒" if p[1] == "∀" else "∧", tup, p[3])
            if temp:
                p[3] = ( "⇒" if p[1] == "∀" else "∧", tup, temp)
                temp = (p[1], tup[1], p[3])
            else:
                temp = (p[1], tup[1], p[3])
        p[0] = temp
    else:
        p[0] = (p[1], p[2], p[3])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    print(f"Detected grouped expression: {p[2]}")
    if type(p[2]) is not int and (is_predicate(p[2]) or is_function(p[2]) or p[2][0] in ["¬", "∧", "∨", "⇒", "⇔", "∀", "∃"]):
        p[0] = p[2]
    else:
        raise Exception(f"Error: Grouping parentheses can only be used with predicates or functions.")



def create_function_rules(function_name, arity, function_type, parentheses= True):
    """Generate grammar rules dynamically based on function definitions."""
    function_alias = symbol_aliases[function_name] if function_name in symbol_aliases else function_name

    if function_type == "prefix":
        if parentheses:
            def p_function_prefix_paren(p):
                print(f"Detected function (prefix with parentheses): {function_name} {p[3]}")
                for args in p[3]:
                    if is_predicate(args):
                        raise Exception(
                            f"Error: Predicate '{args[0]}' cannot be used as an argument for function '{function_name}'.")
                if len(p[3]) != arity:
                    raise Exception(
                        f"Error: Function '{function_name}' expects {arity} arguments, but got {len(p[3])}.")
                p[0] = (function_name, p[3])

            # Dynamically set the docstring
            p_function_prefix_paren.__doc__ = f"expression : {function_alias} LPAREN arguments RPAREN"
            globals()[f"p_function_prefix_{function_alias}"] = p_function_prefix_paren
        else:
            def p_function_prefix(p):
                print(f"Detected function (prefix): {function_name} {p[2]}")
                for args in p[2]:
                    if is_predicate(args):
                        raise Exception(
                            f"Error: Predicate '{args[0]}' cannot be used as an argument for function '{function_name}'.")
                if len(p[2]) != arity:
                    raise Exception(
                        f"Error: Function '{function_name}' expects {arity} arguments, but got {len(p[3])}.")
                p[0] = (function_name, p[2])

            # Dynamically set the docstring
            p_function_prefix.__doc__ = f"expression : {function_alias} arguments"
            globals()[f"p_function_prefix_{function_alias}"] = p_function_prefix

    elif function_type == "infix":
        def p_function_infix(p):
            print(f"Detected function (infix): {p[1]} {p[2]} {p[3]}")
            if is_predicate(p[1]):
                raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for function '{p[2]}'.")

            if is_predicate(p[3]):
                raise Exception(f"Error: Predicate '{p[3]}' cannot be used as an argument for function '{p[2]}'.")
            p[0] = (function_name, p[1], p[3])

        # Dynamically set the docstring
        p_function_infix.__doc__ = f"expression : expression {function_alias} expression"
        globals()[f"p_function_infix_{function_alias}"] = p_function_infix

    elif function_type == "postfix":
        def p_function_postfix(p):
            print(f"Detected function (postfix): {function_name} {p[1]}")
            if is_predicate(p[1]):
                raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for function '{p[2]}'.")
            p[0] = (function_name, p[1])

        # Dynamically set the docstring
        p_function_postfix.__doc__ = f"expression : expression {function_alias}"
        globals()[f"p_function_postfix_{function_alias}"] = p_function_postfix


def create_predicate_rules(predicate_name, arity, predicate_type):
    """Generate grammar rules dynamically based on predicate definitions."""
    predicate_alias = symbol_aliases[predicate_name] if predicate_name in symbol_aliases else predicate_name

    if predicate_type == "prefix":
        def p_predicate_prefix(p):
            print(f"Detected predicate (prefix): {predicate_name} {p[3]}")
            for args in p[3]:
                if is_predicate(args):
                    raise Exception(
                        f"Error: Predicate '{args[0]}' cannot be used as an argument for predicate '{predicate_name}'.")
            if len(p[3]) != arity:
                raise Exception(
                    f"Error: Function '{predicate_name}' expects {arity} arguments, but got {len(p[3])}.")
            p[0] = (predicate_name, p[3])

        # Dynamically set the docstring
        p_predicate_prefix.__doc__ = f"expression : {predicate_alias} LPAREN arguments RPAREN"
        globals()[f"p_predicate_prefix_{predicate_alias}"] = p_predicate_prefix

    elif predicate_type == "infix":
        def p_predicate_infix(p):
            print(f"Detected predicate (infix): {p[1]} {p[2]} {p[3]}")
            if is_predicate(p[1]):
                raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for predicate '{p[2]}'.")

            if is_predicate(p[3]):
                raise Exception(f"Error: Predicate '{p[3]}' cannot be used as an argument for predicate '{p[2]}'.")
            p[0] = (predicate_name, p[1], p[3])

        # Dynamically set the docstring
        p_predicate_infix.__doc__ = f"expression : expression {predicate_alias} expression"
        globals()[f"p_predicate_infix_{predicate_alias}"] = p_predicate_infix

    elif predicate_type == "postfix":
        def p_predicate_postfix(p):
            print(f"Detected predicate (postfix): {predicate_name} {p[1]}")
            if is_predicate(p[1]):
                raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for predicate '{p[2]}'.")
            p[0] = (predicate_name, p[1])

        # Dynamically set the docstring
        p_predicate_postfix.__doc__ = f"expression : expression {predicate_alias}"
        globals()[f"p_predicate_postfix_{predicate_alias}"] = p_predicate_postfix

# Generate rules for functions and predicates
for function_name, details in user_defined_symbols["functions"].items():
    create_function_rules(function_name, details["arity"], details["type"], details["parentheses"] if "parentheses" in details else True)

for predicate_name, details in user_defined_symbols["predicates"].items():
    create_predicate_rules(predicate_name, details["arity"], details["type"])

def p_arguments_single(p):
    """arguments : expression"""
    print(f"Detected single argument: {p[1]}")
    p[0] = [p[1]]

def p_arguments_multiple(p):
    """arguments : expression COMMA arguments"""
    print(f"Detected multiple arguments: {p[1]} {p[2]} {p[3]}")
    p[0] = [p[1]] + p[3]

def p_error(p):
    if p:
        # Find the line where the error occurred
        input_lines = p.lexer.lexdata.splitlines()
        error_line = input_lines[p.lineno - 1]
        # Position in the line
        position = p.lexpos - sum(len(line) + 1 for line in input_lines[:p.lineno - 1])
        print(f"Syntax error at '{p.value}' (position {position}):")
        print(error_line)
        print(" " * position + "^")  # Point to the error
    else:
        print("Syntax error at end of input")

parser = yacc.yacc(debug=False, write_tables=False)


def substitute_user_defined_predicates(shorthand):
    # Extract valid predicates from user_defined_symbols
    predicates = list(user_defined_symbols["predicates"].keys())

    # Create a regex pattern to match variables and any user-defined predicate
    predicate_pattern = "|".join(re.escape(p) for p in predicates)
    variable_pattern = r'[a-zεδ][0-9]*'
    # threshold_pattern = r'[-]?\|?[\w\+\-\*/\^\(\)\., ]+\|?' # Temporary solution
    threshold_pattern = r'[-]?\|?[\w\+\-\*/\^\(\)\., ]\|?'
    # Pattern for matching:
    # - Variables followed by predicate (old case)
    # - Threshold, predicate followed by variables (new case)
    pattern = rf'({threshold_pattern})\s*({predicate_pattern})\s*({variable_pattern}(?:\s*,\s*{variable_pattern})*)|({variable_pattern}(?:\s*,\s*{variable_pattern})*)\s*({predicate_pattern})\s*({threshold_pattern})'
    # Replacement function for matches
    def replacer(match):
        print(match.groups())
        if match.group(1):  # Case 1: Variables, predicate, threshold (variables before predicate)
            variables = match.group(3).split(",")  # Split variables by comma
            predicate = match.group(2)
            threshold = match.group(1)
            return " ∧ ".join(f"{threshold} {predicate} {var.strip()}" for var in variables)
        else:  # Case 2: Threshold, predicate, variables (predicate before variables)
            threshold = match.group(6)
            predicate = match.group(5)
            variables = match.group(4).split(",")  # Split variables by comma
            return " ∧ ".join(f"{var.strip()} {predicate} {threshold}" for var in variables)


    # Perform the substitution
    return re.sub(pattern, replacer, shorthand)


def substitute_chained_predicates(shorthand):
    # Extract valid predicates from user_defined_symbols
    predicates = list(user_defined_symbols["predicates"].keys())

    # Create a regex pattern for variables and any user-defined predicate
    predicate_pattern = "|".join(re.escape(p) for p in predicates)
    pattern = rf'([\w\s,]+)\s*({predicate_pattern})\s*([\w\s,]+(?:\s*({predicate_pattern})\s*[\w\s,]+)*)'

    def replacer(match):
        # Extract leading variable and predicate
        first_var = match.group(1).strip()
        first_pred = match.group(2).strip()
        rest = match.group(3).strip()
        # Split the remaining chain into individual elements
        components = re.split(rf'\s*({predicate_pattern})\s*', rest)

        # Build the conjunctions
        conjunctions = [f"{first_var} {first_pred} {components[0].strip()}"]
        for i in range(1, len(components) - 1, 2):
            left = components[i - 1].strip()
            pred = components[i].strip()
            right = components[i + 1].strip()
            conjunctions.append(f"{left} {pred} {right}")

        return " ∧ ".join(conjunctions)

    # Perform the substitution
    return re.sub(pattern, replacer, shorthand)

def transform_quantifiers(expression):
    return re.sub(r'([∀∃])([a-z]+(?:,[a-z]+)*)', lambda match: ''.join([match.group(1) + var for var in match.group(2).split(',')]), expression)


def add_invisible_multiplication(expression):
    # Temporary solution might need to be improved or removed
    pattern = r'(\d)(?=[a-zεδ][0-9]*)'
    modified_expression = re.sub(pattern, r'\1*', expression)

    return modified_expression

def extract_membership(tup):
    if isinstance(tup, tuple) and tup[0] != "∧":
        return [tup]

    result = []
    if isinstance(tup, tuple):
        for elem in tup[1:]:
            result += extract_membership(elem)
    return result

def get_type(node):
    if node.name in ["∧", "∨", "⇒", "⇔"] or node.name in user_defined_symbols["predicates"]:
        return "Expression type is formula"
    if node.name in ["∀", "∃", "∄", "∃!"]:
        return "Expression type is quantified formula"
    else:
        return "Expression type is term"



# Test the parser
if __name__ == "__main__":
    # data = "(z − y < ε1 ⇒ y − x < ε2 ⇒ z − x ≥ ε1 + ε2)"
    data = "y√z"
    data = substitute_user_defined_predicates(data)
    data = substitute_chained_predicates(data)
    data = transform_quantifiers(data)
    # data = add_invisible_multiplication(data)
    print(data.replace(" ", ""))
    try:
        result = parser.parse(data)
        print(f"Final tree tuple: {result}")
        def build_anytree(data, parent=None):
            if isinstance(data, tuple):
                node = Node(data[0], parent=parent)
                for child in data[1:]:
                    if isinstance(data[1], list):  # If the second element is a list of children
                        for child in data[1]:
                            build_anytree(child, parent=node)
                    else:build_anytree(child, parent=node)
                return node
            else:
                return Node(data, parent=parent)

        anytree_root = build_anytree(result)
        for pre, _, node in RenderTree(anytree_root):
            print(f"{pre}{node.name}")
        print(get_type(anytree_root))
    except Exception as e:
        print(e)
        print("Parsing failed.")

