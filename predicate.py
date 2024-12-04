import re
from anytree import Node, RenderTree


class PredicateLogicParser:
    def __init__(self, proposition):
        self.proposition = proposition.replace(" ", "")
        self.index = 0
        self.length = len(self.proposition)
        self.root = None
        self.variable_regex = re.compile(r"[a-z][0-9]*")
        self.function_symbols = dict()
        self.predicate_symbols = dict()
        self.constant_symbols = set()
        self.quantifiers = {"∀", "∃"}

    def is_variable(self, token):
        return self.variable_regex.match(token) is not None
    def get_function_symbols(self, symbols):
        symbols = symbols.replace(" ", "")
        for symbol in symbols.split(","):
            name, arity = symbol.split("/")
            self.function_symbols[name] = int(arity)

    def get_predicate_symbols(self, symbols):
        symbols=symbols.replace(" ", "")
        for symbol in symbols.split(","):
            name, arity = symbol.split("/")
            self.predicate_symbols[name] = int(arity)

    def get_constant_symbols(self, symbols):
        symbols = symbols.replace(" ", "")
        self.constant_symbols = set(symbols.split(","))

    def current_char(self):
        if self.index < self.length:
            return self.proposition[self.index]
        return None

    def advance(self, steps=1):
        self.index += steps

    def parse_atomic(self):
        match = self.variable_regex.match(self.proposition, self.index)
        if match:
            atomic_token = match.group(0)
            if atomic_token in self.function_symbols or atomic_token in self.constant_symbols:
                return None
            self.advance(len(atomic_token))
            print(f"{atomic_token} is an variable")
            return Node(atomic_token)
        return None

    def parse_constant(self):
        if self.current_char() in self.constant_symbols:
            constant_token = self.current_char()
            self.advance()
            print(f"{constant_token} is a constant")
            return Node(constant_token)
        return None

    def parse_function(self, print_tree=False):
        if self.current_char() in self.function_symbols:
            function_name = self.current_char()
            print(f"Detected function: {function_name}")
            self.advance()
            if self.current_char() == "(":
                self.advance()
                arguments = []
                while self.current_char() != ")":
                    if node := self.parse_expression(print_tree):
                        arguments.append(node)
                        if self.current_char() == ",":
                            self.advance()  # Move past the comma
                    else:
                        return None
                self.advance()
                if len(arguments) != self.function_symbols[function_name]:
                    raise Exception(f"Error: Function {function_name} has {len(arguments)} arguments, but it takes {self.function_symbols[function_name]}")
                print(f"{function_name} is a function with {len(arguments)} arguments")
                function_node = Node(function_name, children=arguments)
                if print_tree:
                    print(f"Created function node: {function_name} with the following children:")
                    for k, child in enumerate(arguments, start=1):
                        print(f"Child {k}:")
                        for pre, _, node in RenderTree(child):
                            print(f"{pre}{node.name}")
                    print()
                    print("Current subtree structure:")
                    for pre, _, node in RenderTree(function_node):
                        print(f"{pre}{node.name}")
                return function_node
            else:
                raise Exception("Error: Missing opening parenthesis for function")
        return None

    def parse_predicate(self, print_tree=False):
        if self.current_char() in self.predicate_symbols:
            predicate_name = self.current_char()
            print(f"Detected predicate: {predicate_name}")
            self.advance()
            if self.current_char() == "(":
                self.advance()
                arguments = []
                while self.current_char() != ")":
                    if node:=self.parse_expression(print_tree):
                        arguments.append(node)
                        if self.current_char() == ",":
                            self.advance() # Move past the comma
                    else:
                        return None
                self.advance()
                if len(arguments) != self.predicate_symbols[predicate_name]:
                    raise Exception(f"Error: Predicate {predicate_name} has {len(arguments)} arguments, but it takes {self.predicate_symbols[predicate_name]}")
                print(f"{predicate_name} is a predicate with {len(arguments)} arguments")
                predicate_node = Node(predicate_name, children=arguments)
                if print_tree:
                    print(f"Created predicate node: {predicate_name} with the following children:")
                    for k, child in enumerate(arguments, start=1):
                        print(f"Child {k}:")
                        for pre, _, node in RenderTree(child):
                            print(f"{pre}{node.name}")
                    print()
                    print("Current subtree structure:")
                    for pre, _, node in RenderTree(predicate_node):
                        print(f"{pre}{node.name}")
                return predicate_node
            else:
                raise Exception("Error: Missing opening parenthesis for predicate")
        return None

    def parse_quantifier(self, print_tree=False):
        if self.current_char() in self.quantifiers:
            quantifier = self.current_char()
            self.advance()
            print(f"{quantifier} is a quantifier")
            if node := self.parse_atomic():
                print(f"Quantified variable: {node.name}")
                if quantifier_expression := self.parse_expression(print_tree):
                    if self.current_char() == ")":
                        quantifier_node = Node(quantifier, children=[node, quantifier_expression])
                        if print_tree:
                            print(f"Created quantifier node: {quantifier_node.name} with the following children:")
                            for k, child in enumerate(quantifier_node.children, start=1):
                                print(f"Child {k}:")
                                for pre, _, node in RenderTree(child):
                                    print(f"{pre}{node.name}")
                            print()
                            print("Current subtree structure:")
                            for pre, _, node in RenderTree(quantifier_node):
                                print(f"{pre}{node.name}")
                        return quantifier_node
            else:
                raise Exception(f"Error: Expected a variable after quantifier got ({self.current_char()}) instead" )
        return None

    def parse_unary(self, print_tree=False):
        if self.current_char() == "(" and self.proposition[self.index+1] == "¬":
            self.advance(2)
            print("Detected opening parenthesis before ¬ operation")
            print("Detected unary connective: ¬")
            if self.current_char() == "(": # Unary connective has a subexpression
                if node := self.parse_expression(print_tree):
                    print("Detected closing parenthesis after ¬ operation")
                    if self.current_char() == ")":
                        self.advance()
                        unary_node = Node("¬", children=[node])  # Create a unary connective node with a child
                        if print_tree:
                            print(f"Created unary connective node: {unary_node.name} with child:")
                            for pre, _, node in RenderTree(node):
                                print(f"{pre}{node.name}")
                            print()
                            print("Current subtree structure:")
                            for pre, _, node in RenderTree(unary_node):
                                print(f"{pre}{node.name}")
                        return unary_node
                    else:
                        raise Exception("Error: Missing closing parenthesis after ¬ operation")
                else:
                    raise Exception("Error: Invalid expression after ¬ connective")
            elif node := self.parse_atomic():
                if self.current_char() == ")":
                    print("Detected closing parenthesis after ¬ operation")
                    self.advance()
                    unary_node = Node("¬", children=[node])
                    if print_tree:
                        print(f"Created unary connective node: {unary_node.name} with child:")
                        for pre, _, node in RenderTree(node):
                            print(f"{pre}{node.name}")
                        print()
                        print("Current subtree structure:")
                        for pre, _, node in RenderTree(unary_node):
                            print(f"{pre}{node.name}")
                    return unary_node
                else:
                    raise Exception("Error: Missing closing parenthesis after ¬ operation")
            else:
                raise Exception("Error: The ¬ connective must be followed by an expression")
        return None

    def parse_binary(self, print_tree=False):
        if self.current_char() == "(":
            print("Detected opening parenthesis for binary operation")
            self.advance()
            if left_node := self.parse_expression(print_tree):
                if left_node.name in self.function_symbols or left_node.name in self.constant_symbols or self.is_variable(left_node.name):
                    raise Exception("Left node of a logical operation cannot be a function, constant, or variable")
                connective = self.current_char()
                if connective in ['⇒', '⇔', '∧', '∨']:
                    print(f"Detected binary connective: {connective}")
                    self.advance()  # Move past the connective
                    right_node = self.parse_expression(print_tree)  # Parse the right expression
                    if right_node:
                        # Create the final binary node with left and right parts
                        binary_node = Node(connective, children=[left_node, right_node])
                    else:
                        raise Exception(f"Error: Invalid expression after {connective} connective")
                    if self.current_char() == ")":
                        print(f"Detected closing parenthesis for {connective} operation")
                        if print_tree:
                            print(f"Created binary connective node: {binary_node.name} with the following children:")
                            for k, child in enumerate(binary_node.children, start=1):
                                print(f"Child {k}:")
                                for pre, _, node in RenderTree(child):
                                    print(f"{pre}{node.name}")
                            print()
                            print("Current subtree structure:")
                            for pre, _, node in RenderTree(binary_node):
                                print(f"{pre}{node.name}")
                        return binary_node
                    else:
                        raise Exception(
                            f"Error: Missing closing parenthesis for {connective if connective != ')' else 'binary'} operation")
            return None

    def parse_expression(self, print_tree=False):
        # Try parsing atomic, unary, or binary and return the Node
        if node := self.parse_atomic():
            return node
        if node := self.parse_constant():
            return node
        if node := self.parse_function(print_tree):
            return node
        if node := self.parse_predicate(print_tree):
            return node
        if node := self.parse_quantifier(print_tree):
            return node
        if node := self.parse_unary(print_tree):
            return node
        if node := self.parse_binary(print_tree):
            return node
        return None

    def parse(self, print_tree=False):
        print(f"Starting parsing for: '{self.proposition}'")
        if len(self.proposition) == 0:
            raise Exception("Error: Empty proposition")
        self.root = self.parse_expression(print_tree)
        if self.root and self.index == self.length:
            print("The string is valid in the given language")
            print("Final tree structure:")
            for pre, _, node in RenderTree(self.root):
                print(f"{pre}{node.name}")
            return self.root  # Return the root of the tree
        else:
            if self.current_char() in ['∧', '∨', '⇒', '⇔']:
                raise Exception("Error: Binary operation is not in parentheses")
            elif self.current_char() == ")" or self.current_char() is None:
                raise Exception("Error: Unbalanced parentheses detected.")
            elif self.current_char() == "¬" and self.index < self.length - 1:
                raise Exception("Error: ¬ operation must be enclosed in parentheses")
            else:
                raise Exception("Error: Invalid structure.")

    def get_type(self, node):
        if node.name in self.function_symbols or node.name in self.constant_symbols or self.is_variable(node.name):
            return "Expression type is term"
        if node.name in self.predicate_symbols or node.name in ["∧", "∨", "⇒", "⇔"]:
            return "Expression type is formula"
        if node.name in self.quantifiers:
            return "Expression type is quantified formula"
        return "Expression type is unknown"


# Example Usage
expression = "P(x, y) ⇔ ∃xR(x, y, z)"
functions = "f/2, g/1, h/3"
predicates = "P/2, Q/2, R/3"
constants = "a, b, c"
parser = PredicateLogicParser(expression)
parser.get_function_symbols(functions)
parser.get_predicate_symbols(predicates)
parser.get_constant_symbols(constants)
try:
    root = parser.parse(print_tree=True)
    print(parser.get_type(root))
except Exception as e:
    print(e)
