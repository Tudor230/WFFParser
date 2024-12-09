import ply.lex as lex
import re
# Define tokens
tokens = (
    'NOT', 'AND', 'OR', 'IMPLIES', 'IFF',
    'FORALL', 'EXISTS',
    'LPAREN', 'RPAREN',
    'VARIABLE', 'CONSTANT', 'COMMA', 'PREDICATE', 'FUNCTION',
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
        "f": {"arity": 1, "type": "prefix"},
        "g": {"arity": 2, "type": "infix"},
        "−": {"arity": 2, "type": "infix"},
        "+": {"arity": 2, "type": "infix"},
        "*": {"arity": 2, "type": "infix"},
        "/": {"arity": 2, "type": "infix"},
    },
    "predicates": {
        "P": {"arity": 2, "type": "prefix"},
        "Q": {"arity": 3, "type": "prefix"},
        "R": {"arity": 3, "type": "prefix"},
        "Z": {"arity": 1, "type": "prefix"},
        "≥": {"arity": 2, "type": "infix"},
        "≤": {"arity": 2, "type": "infix"},
        ">": {"arity": 2, "type": "infix"},
        "<": {"arity": 2, "type": "infix"},
        "≠": {"arity": 2, "type": "infix"},
        "=": {"arity": 2, "type": "infix"},
    }
}

def t_VARIABLE(t):
    r'[a-zε][0-9]*'
    if t.value not in user_defined_symbols:
        t.type = 'VARIABLE'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'  # Matches integers and floating-point numbers
    t.value = int(t.value) if '.' not in t.value else float(t.value)
    if t.value in user_defined_symbols['constants']:
        t.type = 'CONSTANT'  # Treat numbers as constants
    return t



def t_IDENTIFIER(t):
    r'[^¬∧∨⇒⇔∀∃\(\),\s]+'
    # Decide based on user input
    if t.value in user_defined_symbols['constants']:
        t.type = 'CONSTANT'
        return t
    elif t.value in user_defined_symbols['functions']:
        t.type = 'FUNCTION'
        return t
    elif t.value in user_defined_symbols['predicates']:
        t.type = 'PREDICATE'
        return t
    else:
        print(f"Illegal character '{t.value[0]}' at position {t.lexpos}")




# Ignored characters (e.g., whitespace)
t_ignore = ' \t'

# Error handling
def t_error(t):
    r'[^\n]+'
    print(f"Illegal character '{t.value[0]}' at position {t.lexpos}")
    t.lexer.skip(1)

lexer = lex.lex()
