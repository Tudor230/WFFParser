from itertools import product

from anytree import Node, RenderTree


class LogicalWFFParser:
    def __init__(self, proposition):
        self.proposition = proposition.replace(" ", "")
        self.index = 0
        self.length = len(self.proposition)
        self.operation_count = 0
        self.parentheses_balance = 0
        self.root = None

    def is_atomic(self, char):
        return char.isalpha() and len(char) == 1 and char.isupper()

    def current_char(self):
        if self.index < self.length:
            return self.proposition[self.index]
        return None

    def advance(self):
        self.index += 1

    def parse_atomic(self):
        char = self.current_char()
        if char is not None and self.is_atomic(char):
            if self.operation_count:
                print(f"{char} is an atomic subformula")
            else:
                print(f"{char} is an atomic formula")
            self.advance()
            return Node(char)
        return None

    def parse_unary(self):
        if self.current_char() == "(" and self.proposition[self.index + 1] == "¬":
            self.operation_count += 1
            self.parentheses_balance += 1
            print("Detected opening parenthesis before ¬ operation")
            self.advance()
            print("Detected unary connective: ¬")
            self.advance()

            if self.current_char() == "(":
                self.parentheses_balance += 1
                sub_node = self.parse_expression()
                if sub_node:
                    if self.current_char() == ")":
                        self.parentheses_balance -= 1
                        print("Detected closing parenthesis after ¬ operation")
                        self.advance()
                        return Node("¬", children=[sub_node])  # Create a unary node with a child
                    else:
                        raise Exception("Error: Missing closing parenthesis after ¬ operation")
                else:
                    raise Exception("Error: Invalid expression after ¬ connective")
            elif sub_node := self.parse_atomic():
                if self.current_char() == ")":
                    self.parentheses_balance -= 1
                    print("Detected closing parenthesis after ¬ operation")
                    self.advance()
                    return Node("¬", children=[sub_node])  # Create a unary node with a child
                else:
                    raise Exception("Error: Missing closing parenthesis after ¬ operation")
            else:
                raise Exception("Error: The ¬ connective must be followed by an expression")
        return None

    def parse_binary(self):
        if self.current_char() == "(":
            print("Detected opening parenthesis for binary operation")
            self.operation_count += 1
            self.parentheses_balance += 1
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
                            self.parentheses_balance -= 1
                            print(f"Detected closing parenthesis for {connective} operation")
                            self.advance()
                            return Node(connective,
                                        children=[left_node, right_node])  # Create a binary node with two children
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

    def get_variables(self,node):
        if node.is_leaf:
            return {node.name} if self.is_atomic(node.name) else set()
        variables = set()
        for child in node.children:
            variables.update(self.get_variables(child))
        return variables

    def evaluate(self, node, values):
        if node.name == "¬":
            return not self.evaluate(node.children[0], values)
        elif node.name == "∧":
            return self.evaluate(node.children[0], values) and self.evaluate(node.children[1], values)
        elif node.name == "∨":
            return self.evaluate(node.children[0], values) or self.evaluate(node.children[1], values)
        elif node.name == "⇒":
            return not self.evaluate(node.children[0], values) or self.evaluate(node.children[1], values) # P⇒Q=(¬P)∨Q
        elif node.name == "⇔":
            return self.evaluate(node.children[0], values) == self.evaluate(node.children[1], values)
        else:
            return values[node.name]

    def generate_truth_table(self):
        variables = sorted(self.get_variables(self.root))
        truth_values=list(product([False,True],repeat=len(variables)))
        results=[]
        for values in truth_values:
            assignment=dict(zip(variables,values))
            result=self.evaluate(self.root, assignment)
            results.append(result)
        return results

    def check_validity(self):
        truth_table=self.generate_truth_table()
        is_satisfiable= any(result for result in truth_table)
        is_unsatisfiable= all(not result for result in truth_table)
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
    ""
]

for prop in propositions:
    parser = LogicalWFFParser(prop)
    try:
        root = parser.parse()
        if root:
            for pre, _, node in RenderTree(root):
                print(f"{pre}{node.name}")
            print(parser.check_validity())
    except Exception as e:
        print(e)
        print("The string is not a well-formed formula (WFF).")
    print()
