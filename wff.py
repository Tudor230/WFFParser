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
                children=[left_node]
                # Allow consecutive same-type connectives (like ∧∧ or ∨∨)
                while connective in ['∧', '∨']:
                    print(f"Detected binary connective: {connective}")
                    self.advance()  # Move past the connective
                    next_node = self.parse_expression()  # Parse the next expression
                    if next_node:
                        children.append(next_node)
                    else:
                        raise Exception(f"Error: Invalid expression after {connective} connective")
                    if self.current_char() == ")":
                        break
                binary_node = Node(connective, children=children)
                if connective in ['⇒', '⇔']:
                    print(f"Detected binary connective: {connective}")
                    self.advance()  # Move past the connective
                    right_node = self.parse_expression()  # Parse the right expression
                    if right_node:
                        # Create the final binary node with left and right parts
                        binary_node = Node(connective, children=[left_node, right_node])
                    else:
                        raise Exception(f"Error: Invalid expression after {connective} connective")


                if self.current_char() == ")":
                    print(f"Detected closing parenthesis for {connective} operation")
                    self.advance()
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
                    raise Exception(f"Error: Missing closing parenthesis for {connective} operation")
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

    def evaluate_truth_table(self, node, values, intermediary_results=None):
        # Ensure that all required variables are provided in the values dictionary
        if intermediary_results is None:
            intermediary_results = {}
        required_vars = self.get_variables(node)
        missing_vars = required_vars - values.keys()
        if missing_vars:
            raise Exception(f"Missing truth value for {missing_vars}")

        # Check if result for this node is already computed
        if node in intermediary_results:
            return intermediary_results[node]

        # Evaluate based on the type of logical operation in the node
        if node.name == "¬":
            result = not self.evaluate_truth_table(node.children[0], values, intermediary_results)
        elif node.name == "∧":
            result = all(self.evaluate_truth_table(child, values, intermediary_results) for child in node.children)
        elif node.name == "∨":
            result = any(self.evaluate_truth_table(child, values, intermediary_results) for child in node.children)
        elif node.name == "⇒":
            left_result = self.evaluate_truth_table(node.children[0], values, intermediary_results)
            right_result = self.evaluate_truth_table(node.children[1], values, intermediary_results)
            result = not left_result or right_result
        elif node.name == "⇔":
            left_result = self.evaluate_truth_table(node.children[0], values, intermediary_results)
            right_result = self.evaluate_truth_table(node.children[1], values, intermediary_results)
            result = left_result == right_result
        else:
            result = values[node.name]

        intermediary_results[node] = result
        return result

    def get_node_expression(self, node):
        if node.is_leaf:
            return node.name
        elif node.name == "¬":
            return f"(¬{self.get_node_expression(node.children[0])})"
        elif node.name in ["∧", "∨"]:
            # Join expressions of all children with the operator symbol
            child_expressions = [self.get_node_expression(child) for child in node.children]
            return f"({f'{node.name}'.join(child_expressions)})"
        elif node.name in ["⇒", "⇔"]:
            # For binary operators like ⇒ and ⇔, assume exactly two children
            left_expr = self.get_node_expression(node.children[0])
            right_expr = self.get_node_expression(node.children[1])
            return f"({left_expr}{node.name}{right_expr})"
        return node.name

    def get_subexpressions(self, node):
        subexpressions = []

        def traverse(n):
            for child in n.children:
                traverse(child)
            if not n.is_leaf:
                expression = self.get_node_expression(n)
                subexpressions.append(expression)

        traverse(node)
        return subexpressions

    def generate_truth_table(self, do_print=False):
        variables = sorted(self.get_variables(self.root))
        truth_values = list(product([False, True], repeat=len(variables)))
        table = []

        subexpressions = self.get_subexpressions(self.root)
        headers = variables + subexpressions

        # Calculate column width for each header based on its length + 2 spaces
        col_widths = {header: len(header) + 2 for header in headers}

        for values in truth_values:
            assignment = dict(zip(variables, values))
            row = {var: assignment[var] for var in variables}

            intermediary_results = {}

            # Calculate truth values for each subexpression
            for sub_expr in headers[len(variables):]:  # Skip atomic variables in headers
                result = self.evaluate_subexpression(sub_expr, assignment, intermediary_results)
                row[sub_expr] = result

            table.append(row)

        # Print headers with dynamic width alignment
        if do_print:
            header_row = " | ".join(header.center(col_widths[header]) for header in headers)
            print(header_row)
            print("-" * len(header_row))  # Separator line based on total header width

            for row in table:
                row_text = " | ".join(
                    ("T" if row[col] else "F").center(col_widths[col]) for col in headers
                )
                print(row_text)
        return table

    def evaluate_subexpression(self, sub_expr, assignment, intermediary_results):
        # Check if sub_expr is an atomic variable
        if sub_expr in assignment:
            return assignment[sub_expr]

        # Evaluate intermediate expressions
        sub_expr_node = self.find_subexpression_node(sub_expr, self.root)
        return self.evaluate_truth_table(sub_expr_node, assignment, intermediary_results)

    def find_subexpression_node(self, sub_expr, node):
        # Traverse the tree to find the node matching the subexpression
        for n in node.descendants:
            if self.get_node_expression(n) == sub_expr:
                return n
        return node

    def check_validity(self):
        truth_table = self.generate_truth_table()
        formula_values=[entry[list(entry.keys())[-1]] for entry in truth_table]
        print(formula_values)
        is_satisfiable = any(formula_values)
        is_unsatisfiable = all(not value for value in formula_values)
        is_valid = all(formula_values)
        if is_valid:
            return "The formula is valid and satisfiable."
        elif is_unsatisfiable:
            return "The formula is unsatisfiable and invalid."
        elif is_satisfiable:
            return "The formula is satisfiable but invalid."


# Testing with propositions
propositions = [
    # "(¬(P ∧ Q))",
    # "(¬P ∨ (Q ∧ R))",
    # "(¬(¬P)",
    # "((P ∧ Q))",
    # "(P ∧ Q)",
    # "(P ∨ Q ∨ R ∨ T ∨ Q)",
    # "(P ∧ Q)¬",
    # "(P ∧ Q ∧ R)",
    # "(¬(P ∧ Q ∧ R))",
    # "(((P ⇒ Q) ∨ S) ⇔ T)",
    # "((P ⇒ (Q ∧ (S ⇒ T))))",
    # "(¬(B(¬Q)) ∧ R)",
    "(P ∧ ((¬Q) ∧ (¬(¬(Q ⇔ (¬R))))))",
    # "(((P ∨ Q) ⇒ (¬(P ∨ Q))) ∧ (P ∨ (¬(¬Q))))",
    # "(N∧M∧J)",
    # "P",
    # "(P∧(¬P))",
    # "(P∨(¬P))"
]

values = [
    {"P": True, "Q": False, "R": True},
    {"P": True, "Q": True, "R": True},
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
            parser.generate_truth_table(do_print=True)
            try:
                for value in values:
                    result = parser.evaluate_truth_table(root, value)
                    print(f"The truth value of the proposition with {value} interpretation is {result}")
            except Exception as e:
                print(f"Error during evaluation: {e}")
    except Exception as e:
        print(e)
        print("The string is not a well-formed formula (WFF).")
    print()
