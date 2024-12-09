import ply.lex as lex
import re

# Define tokens
static_tokens = (
    'NOT', 'AND', 'OR', 'IMPLIES', 'IFF',
    'FORALL', 'EXISTS',
    'LPAREN', 'RPAREN',
    'VARIABLE', 'CONSTANT', 'COMMA',
    'NUMBER'
)

# Token definitions
t_NOT = r'¬'
t_AND = r'∧'
t_OR = r'∨'
t_IMPLIES = r'⇒'
t_IFF = r'⇔'
t_FORALL = r'∀'
t_EXISTS = r'∃'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','

user_defined_symbols = {
    "constants": {"a", "b", "c", 4},  # Constants as a set
    "functions": {
        "f": {"arity": 1, "type": "prefix", "precedence": 1},
        "g": {"arity": 2, "type": "infix", "precedence": 1},
        "−": {"arity": 2, "type": "infix", "precedence": 2},
        "+": {"arity": 2, "type": "infix", "precedence": 2},
        "*": {"arity": 2, "type": "infix", "precedence": 3},
        "/": {"arity": 2, "type": "infix", "precedence": 3},
    },
    "predicates": {
        "P": {"arity": 2, "type": "prefix", "precedence": 1},
        "Q": {"arity": 3, "type": "prefix", "precedence": 1},
        "R": {"arity": 3, "type": "prefix", "precedence": 1},
        "Z": {"arity": 1, "type": "prefix", "precedence": 1},
        "≥": {"arity": 2, "type": "infix", "precedence": 1},
        "≤": {"arity": 2, "type": "infix", "precedence": 1},
        ">": {"arity": 2, "type": "infix", "precedence": 1},
        "<": {"arity": 2, "type": "infix", "precedence": 1},
        "≠": {"arity": 2, "type": "infix", "precedence": 1},
        "=": {"arity": 2, "type": "infix", "precedence": 1},
    }
}

symbol_aliases = {
    '+': 'PLUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '−': 'MINUS',
    '≥': 'GEQ',
    '≤': 'LEQ',
    '>': 'GT',
    '<': 'LT',
    '≠': 'NEQ',
    '=': 'EQ',
}

sorted_functions = sorted(user_defined_symbols["functions"].items(), key=lambda item: len(item[0]), reverse=True)

# Sort predicates by the length of their names in descending order
sorted_predicates = sorted(user_defined_symbols["predicates"].items(), key=lambda item: len(item[0]), reverse=True)

# Update the user_defined_symbols dictionary with the sorted functions and predicates
user_defined_symbols["functions"] = dict(sorted_functions)
user_defined_symbols["predicates"] = dict(sorted_predicates)

tokens = list(static_tokens) + list(symbol_aliases.values())

tokens += [func for func in user_defined_symbols["functions"] if func not in symbol_aliases]
tokens += [pred for pred in user_defined_symbols["predicates"] if pred not in symbol_aliases]
tokens= tuple(tokens)



for symbol, alias in symbol_aliases.items():
    globals()[f"t_{alias}"] = re.escape(symbol)


for function in user_defined_symbols["functions"]:
    if function not in symbol_aliases:
        globals()[f"t_{function}"] = function

for predicate in user_defined_symbols["predicates"]:
    if predicate not in symbol_aliases:
        globals()[f"t_{predicate}"] = predicate


def generate_constant_token_function():
    # Escape constants for regex and join with `|` to create a regex pattern
    constants = user_defined_symbols["constants"]
    pattern = r'(?:' + '|'.join(re.escape(str(constant)) for constant in constants) + r')'
    # Define the token function
    def CONSTANT(t):
        t.type = 'CONSTANT'  # Set the token type explicitly
        return t

    # Attach the dynamically created regex to the function
    CONSTANT.__doc__ = pattern  # PLY uses the docstring for the regex
    globals()['t_CONSTANT'] = CONSTANT  # Assign the function to the global namespace

def generate_variable_token_function():
    # Gather all used names from constants and functions
    used_names = set(user_defined_symbols["constants"])
    used_names.update(user_defined_symbols["functions"].keys())

    # Create a regex pattern for valid variable names (lowercase letter followed by digits)
    # Exclude used names
    pattern = r'[a-zε][0-9]*'
    excluded_pattern = r'\b(?:' + '|'.join(re.escape(str(name)) for name in used_names) + r')\b'
    final_pattern = f"(?!{excluded_pattern}){pattern}" if used_names else pattern
    # Define the token function
    def VARIABLE(t):
        t.type = 'VARIABLE'  # Set the token type explicitly
        return t

    # Attach the dynamically created regex to the function
    VARIABLE.__doc__ = final_pattern  # PLY uses the docstring for the regex
    globals()['t_VARIABLE'] = VARIABLE  # Assign the function to the global namespace

generate_constant_token_function()
generate_variable_token_function()


def t_NUMBER(t):
    r'\d+(\.\d+)?'  # Matches integers and floating-point numbers
    t.value = int(t.value) if '.' not in t.value else float(t.value)
    if t.value in user_defined_symbols['constants']:
        t.type = 'CONSTANT'  # Treat numbers as constants
    return t


# Ignored characters (e.g., whitespace)
t_ignore = ' \t'

# Error handling
def t_error(t):
    r'[^\n]+'
    print(f"Illegal character '{t.value[0]}' at position {t.lexpos}")
    t.lexer.skip(1)

lexer = lex.lex()
