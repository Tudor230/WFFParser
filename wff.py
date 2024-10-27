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
            raise Exception("Error: Invalid structure.")


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
    except Exception as e:
        print(e)
        print("The string is not a well-formed formula (WFF).")
    print()
