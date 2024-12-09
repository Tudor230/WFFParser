import ply.yacc as yacc
from lexer import tokens, user_defined_symbols

precedence_tuple = (
    ('right', 'IMPLIES', 'IFF'),  # Right-associative for ⇒ and ⇔
    ('left', 'OR'),               # ∨ has lower precedence than ∧
    ('left', 'AND'),
    ('left', 'FUNCTION', 'PREDICATE'),  # Functions and predicates have lower precedence
    ('left', 'NOT'),             # ¬ is right-associative
)

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
    p[0] = (p[2], p[1], p[3])

def p_expression_unary(p):
    """expression : NOT expression"""
    p[0] = (p[1], p[2])

def p_expression_quantifier(p):
    """expression : FORALL VARIABLE expression
                  | EXISTS VARIABLE expression """
    p[0] = (p[1], p[2], p[3])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_predicate_prefix(p):
    """expression : PREDICATE LPAREN arguments RPAREN"""
    predicate_name = p[1]
    arguments = p[3]
    expected_arity = user_defined_symbols['predicates'].get(predicate_name, -1)

    # Check if the number of arguments matches the expected arity
    if expected_arity != -1 and len(arguments) == expected_arity:
        p[0] = (predicate_name, arguments)  # Store the predicate and its arguments
    else:
        raise Exception(f"Error: Predicate '{predicate_name}' expects {expected_arity} arguments, but got {len(arguments)}.")

def p_predicate_infix(p):
    """expression : expression PREDICATE expression"""
    p[0] = (p[2], p[1], p[3])

def p_predicate_postfix(p):
    """expression : expression PREDICATE"""
    p[0] = (p[2], p[1])

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

def p_function_prefix(p):
    """expression : FUNCTION LPAREN arguments RPAREN"""
    function_name = p[1]
    arguments = p[3]

    expected_arity = user_defined_symbols['functions'].get(function_name, -1)

    for arg in arguments:
        if is_predicate(arg):
            raise Exception(
                f"Error: Predicate '{arg[0]}' cannot be used as an argument for function '{function_name}'.")
    # Check if the number of arguments matches the expected arity
    if expected_arity != -1 and len(arguments) == expected_arity:
        p[0] = (function_name, arguments)  # Store the function and its arguments
    else:
        raise Exception(f"Error: Function '{function_name}' expects {expected_arity} arguments, but got {len(arguments)}.")

def p_function_infix(p):
    """expression : expression FUNCTION expression"""
    if is_predicate(p[1]):
        raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for function '{p[2]}'.")

    if is_predicate(p[3]):
        raise Exception(f"Error: Predicate '{p[3]}' cannot be used as an argument for function '{p[2]}'.")
    p[0] = (p[2], p[1], p[3])

def p_function_postfix(p):
    """expression : expression FUNCTION"""
    if is_predicate(p[1]):
        raise Exception(f"Error: Predicate '{p[1]}' cannot be used as an argument for function '{p[2]}'.")
    p[0] = (p[2], p[1])

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
