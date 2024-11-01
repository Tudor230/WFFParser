from itertools import product
import re
from anytree import Node, RenderTree


class LogicalWFFParser:
    def __init__(self, proposition):
        self.proposition = proposition.replace(" ", "")
        self.index = 0
        self.length = len(self.proposition)
        self.operation_count = 0
        self.root = None
        self.atomic_regex = re.compile(r"[A-Z][0-9]*")  # Regex for atomic propositions

    def is_atomic(self, char):
        return bool(self.atomic_regex.fullmatch(char))

    def current_char(self):
        if self.index < self.length:
            return self.proposition[self.index]
        return None

    def advance(self, steps=1):
        self.index += steps

    def parse_atomic(self):
        match = self.atomic_regex.match(self.proposition, self.index)
        if match:
            atomic_token = match.group(0)
            self.advance(len(atomic_token))
            if self.operation_count:
                print(f"{atomic_token} is an atomic subformula")
            else:
                print(f"{atomic_token} is an atomic formula")
            return Node(atomic_token)
        return None

    def parse_unary(self):
        if self.current_char() == "(" and self.proposition[self.index + 1] == "¬":
            self.operation_count += 1
            print("Detected opening parenthesis before ¬ operation")
            self.advance()
            print("Detected unary connective: ¬")
            self.advance()

            if self.current_char() == "(":
                sub_node = self.parse_expression()
                if sub_node:
                    if self.current_char() == ")":
                        print("Detected closing parenthesis after ¬ operation")
                        self.advance()
                        unary_node = Node("¬", children=[sub_node])  # Create a unary connective node with a child
                        print(f"Created unary connective node: {unary_node.name} with child:")
                        for pre, _, node in RenderTree(sub_node):
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
            elif sub_node := self.parse_atomic():
                if self.current_char() == ")":
                    print("Detected closing parenthesis after ¬ operation")
                    self.advance()
                    unary_node = Node("¬", children=[sub_node])  # Create a unary connective node with a child
                    print(f"Created unary connective node: {unary_node.name} with child: {sub_node.name}")
                    print("Current subtree structure:")
                    for pre, _, node in RenderTree(unary_node):
                        print(f"{pre}{node.name}")
                    return unary_node
                else:
                    raise Exception("Error: Missing closing parenthesis after ¬ operation")
            else:
                raise Exception("Error: The ¬ connective must be followed by an expression")
        return None

    def parse_binary(self):
        if self.current_char() == "(":
            print("Detected opening parenthesis for binary operation")
            self.operation_count += 1
            self.advance()

            left_node = self.parse_expression()
            if left_node:
                connective = self.current_char()
                if connective in ['∧', '∨', '⇒', '⇔']:
                    print(f"Detected binary connective: {connective}")
                    self.advance()

                    right_node = self.parse_expression()
                    if right_node:
                        if self.current_char() == ")":
                            print(f"Detected closing parenthesis for {connective} operation")
                            self.advance()
                            binary_node = Node(connective, children=[left_node, right_node])  # Create a binary connective node with two children
                            print(f"Created binary connective node: {binary_node.name} with the following children:")
                            k = 1
                            for i in binary_node.children:
                                print(f"Child {k}:")
                                for pre, _, node in RenderTree(i):
                                    print(f"{pre}{node.name}")
                                k+=1
                            print()
                            print("Current subtree structure:")
                            for pre, _, node in RenderTree(binary_node):
                                print(f"{pre}{node.name}")
                            return binary_node
                        else:
                            raise Exception(f"Error: Missing closing parenthesis for {connective} operation")
                    else:
                        raise Exception(f"Error: Invalid expression after {connective} connective")
                else:
                    raise Exception("Error: Expected binary connective inside parentheses")
        return None

    def parse_expression(self):
        # Try parsing atomic, unary, or binary and return the Node
        if node := self.parse_atomic():
            return node
        if node := self.parse_unary():
            return node
        if node := self.parse_binary():
            return node
        return None

    def parse(self):
        print(f"Starting parsing for: '{self.proposition}'")
        if len(self.proposition) == 0:
            raise Exception("Error: Empty proposition")

        # Parse and store the root of the tree
        self.root = self.parse_expression()

        # If we reach the end of the proposition and parsing was successful
        if self.root and self.index == self.length:
            print("The string is a well-formed formula (WFF).")
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

    def get_variables(self, node):
        # Get all unique atomic variables from the node's leaves
        vars_found = {leaf.name for leaf in node.leaves}
        return vars_found

    def evaluate(self, node, values):
        required_vars = self.get_variables(node)
        missing_vars = required_vars - values.keys()
        if missing_vars:
            raise Exception(f"Missing truth value for {missing_vars}")
        if node.name == "¬":
            return not self.evaluate(node.children[0], values)
        elif node.name == "∧":
            return self.evaluate(node.children[0], values) and self.evaluate(node.children[1], values)
        elif node.name == "∨":
            return self.evaluate(node.children[0], values) or self.evaluate(node.children[1], values)
        elif node.name == "⇒":
            return not self.evaluate(node.children[0], values) or self.evaluate(node.children[1], values)  # P⇒Q=(¬P)∨Q
        elif node.name == "⇔":
            return self.evaluate(node.children[0], values) == self.evaluate(node.children[1], values)
        else:
            return values[node.name]

    def generate_truth_table(self):
        variables = sorted(self.get_variables(self.root))
        truth_values = list(product([False, True], repeat=len(variables)))
        results = []
        for values in truth_values:
            assignment = dict(zip(variables, values))
            result = self.evaluate(self.root, assignment)
            results.append(result)
        return results

    def check_validity(self):
        truth_table = self.generate_truth_table()
        is_satisfiable = any(result for result in truth_table)
        is_unsatisfiable = all(not result for result in truth_table)
        is_valid = all(result for result in truth_table)
        if is_valid:
            return "The formula is valid and satisfiable."
        elif is_unsatisfiable:
            return "The formula is unsatisfiable and invalid."
        elif is_satisfiable:
            return "The formula is satisfiable but invalid."


# Testing with propositions
propositions = [
    "(¬(P ∧ Q))",
    "(¬P ∨ (Q ∧ R))",
    "(¬(¬P)",
    "((P ∧ Q))",
    "(P ∧ Q)",
    "(P ∨ (Q ∧ R))",
    "(P ∧ Q)¬",
    "(P ∨ (Q ∧ R)))",
    "¬(P ∨ (Q ∧ R)",
    "(((P ⇒ Q) ∨ S) ⇔ T)",
    "((P ⇒ (Q ∧ (S ⇒ T))))",
    "(¬(B(¬Q)) ∧ R)",
    "(P ∧ ((¬Q) ∧ (¬(¬(Q ⇔ (¬R))))))",
    "((P ∨ Q) ⇒ ¬(P ∨ Q)) ∧ (P ∨ (¬(¬Q)))",
    "(N∧M∧J)",
    "P",
    "(P∧(¬P))",
    "(P∨(¬P))"
]

values = [
    {"P": True, "Q": False},
    {"P": True, "Q": True}
]

for prop in propositions:
    parser = LogicalWFFParser(prop)
    try:
        root = parser.parse()
        if root:
            print("Final tree structure:")
            for pre, _, node in RenderTree(root):
                print(f"{pre}{node.name}")  # Using RenderTree to print the subtree
            print(parser.check_validity())
            try:
                for value in values:
                    result = parser.evaluate(root, value)
                    print(f"The truth value of the proposition with {value} interpretation is {result}")
            except Exception as e:
                print(f"Error during evaluation: {e}")
    except Exception as e:
        print(e)
        print("The string is not a well-formed formula (WFF).")
    print()
