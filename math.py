from collections import defaultdict
import ply.yacc as yacc
from lexer import tokens, user_defined_symbols, symbol_aliases
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
precedence = static_precedence + precedence
precedence = tuple(precedence)

def is_predicate(expr):
    """Check if the given expression is a predicate."""
    return isinstance(expr, tuple) and expr[0] in user_defined_symbols['predicates']

def p_start(p):
    """start : expression"""
    p[0] = p[1]

def p_expression_base(p):
    """expression : VARIABLE
                  | CONSTANT
                  | NUMBER"""
    p[0] = p[1]

def p_expression_binary(p):
    """expression : expression AND expression
                  | expression OR expression
                  | expression IMPLIES expression
                  | expression IFF expression"""
    if (is_predicate(p[1]) or p[1][0] in ["¬", "∧", "∨", "⇒", "⇔"]) and (is_predicate(p[3]) or p[3][0] in ["¬", "∧", "∨", "⇒", "⇔"]):
        p[0] = (p[2], p[1], p[3])
    else:
        raise Exception(f"Error: Binary logical operators can only be used between predicates.")

def p_expression_unary(p):
    """expression : NOT expression"""
    if is_predicate(p[2]) or p[2][0] in ["¬", "∧", "∨", "⇒", "⇔"]:
        p[0] = (p[1], p[2])
    else:
        raise Exception(f"Error: Unary logical operator 'NOT' can only be used with predicates.")

def p_expression_quantifier(p):
    """expression : FORALL VARIABLE expression
                  | EXISTS VARIABLE expression """
    p[0] = (p[1], p[2], p[3])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def create_function_rules(function_name, arity, function_type):
    """Generate grammar rules dynamically based on function definitions."""
    function_alias = symbol_aliases[function_name] if function_name in symbol_aliases else function_name

    if function_type == "prefix":
        def p_function_prefix(p):
            for args in p[3]:
                if is_predicate(args):
                    raise Exception(
                        f"Error: Predicate '{args[0]}' cannot be used as an argument for function '{function_name}'.")
            if len(p[3]) != arity:
                raise Exception(
                    f"Error: Function '{function_name}' expects {arity} arguments, but got {len(p[3])}.")
            p[0] = (function_name, p[3])

        # Dynamically set the docstring
        p_function_prefix.__doc__ = f"expression : {function_alias} LPAREN arguments RPAREN"
        globals()[f"p_function_prefix_{function_alias}"] = p_function_prefix

    elif function_type == "infix":
        def p_function_infix(p):
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
            if is_predicate(p[1]):
                raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for predicate '{p[2]}'.")
            p[0] = (predicate_name, p[1])

        # Dynamically set the docstring
        p_predicate_postfix.__doc__ = f"expression : expression {predicate_alias}"
        globals()[f"p_predicate_postfix_{predicate_alias}"] = p_predicate_postfix

# Generate rules for functions and predicates
for function_name, details in user_defined_symbols["functions"].items():
    create_function_rules(function_name, details["arity"], details["type"])

for predicate_name, details in user_defined_symbols["predicates"].items():
    create_predicate_rules(predicate_name, details["arity"], details["type"])


def p_invisible_multiplication(p):
    """expression : NUMBER NUMBER
                    | NUMBER VARIABLE
                    | NUMBER CONSTANT
                    | NUMBER LPAREN expression RPAREN
                    | VARIABLE NUMBER
                    | VARIABLE VARIABLE
                    | VARIABLE CONSTANT
                    | VARIABLE LPAREN expression RPAREN
                    | CONSTANT NUMBER
                    | CONSTANT VARIABLE
                    | CONSTANT CONSTANT
                    | CONSTANT LPAREN expression RPAREN"""
    p[0] = ('*', p[1], p[2])

def p_arguments_single(p):
    """arguments : expression"""
    p[0] = [p[1]]

def p_arguments_multiple(p):
    """arguments : expression COMMA arguments"""
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

# Test the parser
if __name__ == "__main__":
    data = "(z − y < ε1 ⇒ y − x < ε2 ⇒ z − x ≥ ε1 + ε2)"
    result = parser.parse(data)
    print(result)
