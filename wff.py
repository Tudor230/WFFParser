from itertools import product
import re
from operator import truth

from ShuntingYard import ShuntingYardConverter
from anytree import Node, RenderTree


class LogicalWFFParser:
    def __init__(self, proposition):
        self.proposition = proposition.replace(" ", "")
        self.index = 0
        self.length = len(self.proposition)
        self.operation_count = 0
        self.root = None
        self.atomic_regex = re.compile(r"[A-Z][0-9]*|⊤|⊥")  # Regex for atomic propositions

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

    def parse_unary(self, print_tree):
        if self.current_char() == "(" and self.proposition[self.index + 1] == "¬":
            self.operation_count += 1
            print("Detected opening parenthesis before ¬ operation")
            self.advance()
            print("Detected unary connective: ¬")
            self.advance()

            if self.current_char() == "(":
                sub_node = self.parse_expression(print_tree)
                if sub_node:
                    if self.current_char() == ")":
                        print("Detected closing parenthesis after ¬ operation")
                        self.advance()
                        unary_node = Node("¬", children=[sub_node])  # Create a unary connective node with a child
                        if print_tree:
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
                    if print_tree:
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

    def parse_binary(self, print_tree):
        if self.current_char() == "(":
            print("Detected opening parenthesis for binary operation")
            self.operation_count += 1
            self.advance()

            left_node = self.parse_expression(print_tree)
            if left_node:
                connective = self.current_char()
                children=[left_node]
                # Allow consecutive same-type connectives (like ∧∧ or ∨∨)
                while connective in ['∧', '∨']:
                    print(f"Detected binary connective: {connective}")
                    self.advance()  # Move past the connective
                    next_node = self.parse_expression(print_tree)  # Parse the next expression
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
                    right_node = self.parse_expression(print_tree)  # Parse the right expression
                    if right_node:
                        # Create the final binary node with left and right parts
                        binary_node = Node(connective, children=[left_node, right_node])
                    else:
                        raise Exception(f"Error: Invalid expression after {connective} connective")

                if self.current_char() == ")" and connective !=")":
                    print(f"Detected closing parenthesis for {connective} operation")
                    self.advance()
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
                    raise Exception(f"Error: Missing closing parenthesis for {connective if connective != ')' else 'binary'} operation")
        return None

    def parse_expression(self,print_tree):
        # Try parsing atomic, unary, or binary and return the Node
        if node := self.parse_atomic():
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

        # Parse and store the root of the tree
        self.root = self.parse_expression(print_tree)

        # If we reach the end of the proposition and parsing was successful
        if self.root and self.index == self.length:
            print("The string is a well-formed formula (WFF).")
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
        always_true = '⊤' in variables
        always_false = '⊥' in variables
        free_variables = [var for var in variables if var not in ['⊤', '⊥']]
        truth_values = list(product([False, True], repeat=len(free_variables)))
        table = []

        subexpressions = self.get_subexpressions(self.root)
        headers = free_variables + (['⊥'] if always_false else []) + (['⊤'] if always_true else []) + subexpressions

        # Calculate column width for each header based on its length + 2 spaces
        col_widths = {header: len(header) + 2 for header in headers}

        for values in truth_values:
            assignment = dict(zip(free_variables, values))
            if always_true:
                assignment['⊤'] = True
            if always_false:
                assignment['⊥'] = False
            row = {var: assignment[var] for var in variables}
            if always_true:
                row['⊤'] = True
            if always_false:
                row['⊥'] = False
            intermediary_results = {}

            # Calculate truth values for each subexpression
            for sub_expr in headers[len(variables):]:  # Skip atomic variables in headers
                result = self.evaluate_subexpression(sub_expr, assignment, intermediary_results)
                row[sub_expr] = result

            table.append(row)

        # Print headers with dynamic width alignment
        if do_print:
            self.print_truth_table(table)
        return table

    def print_truth_table(self, table):
        if not table:
            print("No data to display.")
            return

        headers = list(table[0].keys())
        col_widths = {header: len(header) + 2 for header in headers}

        header_row = " | ".join(header.center(col_widths[header]) for header in headers)
        print(header_row)
        print("-" * len(header_row))  # Separator line based on total header width

        for row in table:
            row_text = " | ".join(
                ("T" if row[col] else "F").center(col_widths[col]) for col in headers
            )
            print(row_text)

    def evaluate_subexpression(self, sub_expr, assignment, intermediary_results):
        # Check if sub_expr is an atomic variable
        if sub_expr in assignment:
            return assignment[sub_expr]

        # Evaluate intermediate expressions
        sub_expr_node = self.find_subexpression_node(sub_expr, self.root)
        return self.evaluate_truth_table(sub_expr_node, assignment, intermediary_results)

    def find_subexpression_node(self, sub_expr, node):
        stack = [node]  # Initialize a stack for depth-first search
        while stack:
            current_node = stack.pop()
            # Check if the current node matches the exact expression
            if self.get_node_expression(current_node) == sub_expr:
                return current_node
            # Extend the stack with children nodes
            stack.extend(current_node.children)
        return None

    def check_validity(self):
        truth_table = self.generate_truth_table()
        formula_values = [entry[list(entry.keys())[-1]] for entry in truth_table]
        is_satisfiable = any(formula_values)
        is_unsatisfiable = all(not value for value in formula_values)
        is_valid = all(formula_values)
        if is_valid:
            return "The formula is valid and satisfiable."
        elif is_unsatisfiable:
            return "The formula is unsatisfiable and invalid."
        elif is_satisfiable:
            return "The formula is satisfiable but invalid."

    def check_equivalence(self, other_parser):
        self_table = self.generate_truth_table()
        other_table = other_parser.generate_truth_table()

        self_vars = set(self.get_variables(self.root))
        other_vars = set(other_parser.get_variables(other_parser.root))

        common_vars = self_vars.intersection(other_vars)

        # Build filtered truth tables based on common variables
        filtered_self_table = [
            {var: row[var] for var in common_vars} | {'result': self.evaluate_truth_table(self.root, row)}
            for row in self_table
        ]

        filtered_other_table = [
            {var: row[var] for var in common_vars} | {
                'result': other_parser.evaluate_truth_table(other_parser.root, row)}
            for row in other_table
        ]
        # Compare the truth values of both tables row by row based on the common variable assignments
        # Create a mapping of results based on common variables for self
        self_result_map = {tuple(row[var] for var in common_vars): row['result'] for row in filtered_self_table}
        other_result_map = {tuple(row[var] for var in common_vars): row['result'] for row in filtered_other_table}
        for key in self_result_map:
            if key in other_result_map:
                if self_result_map[key] != other_result_map[key]:
                    return False
            else:
                return False
        return True

    def check_consequence(self, premises, conclusion):
        # Generate the truth table for the given premises and conclusion
        headers,truth_table = self.generate_consequence_truth_table(premises, conclusion)
        self.print_consequence_truth_table(headers, truth_table)
        for row in truth_table:
            premises_true = True
            for premise in premises:
                if row[premise] is False:
                    premises_true = False
                    break
            if premises_true and row[conclusion] is False:
                return False
        return True

    def generate_consequence_truth_table(self, premises, conclusion):
        # Parse the premises and conclusion
        parsed_premises = [LogicalWFFParser(premise).parse() for premise in premises]
        parsed_conclusion = LogicalWFFParser(conclusion).parse()
        # Gather all variables from premises and conclusion
        all_vars = set()
        for premise in parsed_premises:
            all_vars.update(self.get_variables(premise))
        all_vars.update(self.get_variables(parsed_conclusion))

        # Generate truth value combinations for all variables
        truth_values = list(product([False, True], repeat=len(all_vars)))
        table = []
        # Create headers for the truth table
        headers = sorted(all_vars)
        subexpressions = []

        # Collect subexpressions for premises
        for premise in parsed_premises:
            subexpressions.extend(self.get_subexpressions(premise))

        # Add subexpressions for conclusion
        subexpressions.extend(self.get_subexpressions(parsed_conclusion))
        headers.extend(subexpressions)

        # Evaluate each combination of truth values
        for values in truth_values:
            assignment = dict(zip(sorted(all_vars), values))
            # Calculate truth values for premises and conclusion
            row = {var: assignment[var] for var in sorted(all_vars)}
            # Calculate truth values for each subexpression
            intermediary_results = {}
            for sub_expr in subexpressions:
                sub_expr_node = None
                # Try to find the subexpression node in each premise first
                for premise in parsed_premises:
                    sub_expr_node = self.find_subexpression_node(sub_expr, premise)
                    if sub_expr_node:
                        break

                # If not found in premises, try the conclusion
                if not sub_expr_node:
                    sub_expr_node = self.find_subexpression_node(sub_expr, parsed_conclusion)

                # Evaluate the subexpression if the node is found
                if sub_expr_node:
                    row[sub_expr] = self.evaluate_truth_table(sub_expr_node, assignment, intermediary_results)

            # Add the row to the truth table
            table.append(row)
        return headers, table

    def print_consequence_truth_table(self, headers, table):

        if not table:
            print("No data to display.")
            return

        col_widths = {header: len(header) + 2 for header in headers}

        # Print headers
        header_row = " | ".join(header.center(col_widths[header]) for header in headers)
        print(header_row)
        print("-" * len(header_row))

        # Print rows
        for row in table:
            row_text = " | ".join(
                ("T" if row[col] else "F").center(col_widths[col]) for col in headers
            )
            print(row_text)

        print()


def main():
    print("=== Well Formed Logical Formula Console Interface  ===")
    while True:
        print("\nPlease select an option:")
        print("1. Check if a formula is valid or satisfiable")
        print("2. Check if two formulas are equivalent")
        print("3. Generate a truth table for a formula")
        print("4. Check truth value of a formula with specific values")
        print("5. Check if multiple formulas entail a consequence")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")
        if choice == "1":
            proposition = input("Enter a proposition: ")
            converter = ShuntingYardConverter(proposition)
            try:
                converted_proposition=converter.convert()
                parser = LogicalWFFParser(converted_proposition)
                root=parser.parse(print_tree=True)
                if root:
                    print("Final tree structure:")
                    for pre, _, node in RenderTree(root):
                        print(f"{pre}{node.name}")  # Using RenderTree to print the subtree
                    print()
                    print(parser.check_validity())
            except Exception as e:
                print(e)
                print("The string is not a well-formed formula.")
        elif choice == "2":
            proposition1 = input("Enter the first formula: ")
            proposition2 = input("Enter the second formula: ")
            converter1 = ShuntingYardConverter(proposition1)
            converter2 = ShuntingYardConverter(proposition2)

            try:
                converted_proposition1=converter1.convert()
                converted_proposition2=converter2.convert()
                parser1 = LogicalWFFParser(converted_proposition1)
                parser2 = LogicalWFFParser(converted_proposition2)
                root1 = parser1.parse()
                root2 = parser2.parse()

                equivalence_result = parser1.check_equivalence(parser2)
                print(f"\nTruth Table for '{proposition1}':")
                parser1.generate_truth_table(do_print=True)

                print(f"\nTruth Table for '{proposition2}':")
                parser2.generate_truth_table(do_print=True)
                print(
                    "The two formulas are equivalent." if equivalence_result else "The two formulas are not equivalent.")
            except Exception as e:
                print(e)
        elif choice == "3":
            proposition = input("Enter a formula to generate a truth table: ")
            converter = ShuntingYardConverter(proposition)
            try:
                converted_proposition = converter.convert()
                parser = LogicalWFFParser(converted_proposition)
                root = parser.parse()
                parser.generate_truth_table(do_print=True)
            except Exception as e:
                print(e)
        elif choice == "4":
            proposition = input("Enter a proposition: ")
            try:
                converter = ShuntingYardConverter(proposition)
                converted_proposition = converter.convert()
                parser = LogicalWFFParser(converted_proposition)
                root = parser.parse()
                values = {}
                while True:
                    variable = input("Enter a variable name (or type 'done' to finish): ")
                    if variable.lower() == 'done':
                        break
                    if not variable.isupper():
                        print("Variable names must be uppercase. Please enter an uppercase variable name.")
                        continue
                    boolean_value = input(f"Enter True or False for {variable}: ")
                    if boolean_value.lower() == 'true':
                        values[variable] = True
                    elif boolean_value.lower() == 'false':
                        values[variable] = False
                    else:
                        print("Invalid input. Please enter 'True' or 'False'.")

                # Evaluate the truth value of the proposition
                result = parser.evaluate_truth_table(root, values)
                print(f"The truth value of the proposition '{proposition}' with the given values is: {result}")

            except Exception as e:
                print(e)
                print("The string is not a well-formed formula or invalid values were provided.")
        elif choice == "5":
            premises = input("Enter premises (separated by commas): ").replace(' ', '').split(',')
            conclusion = input("Enter the conclusion: ")

            try:
                converted_premises = []
                for premise in premises:
                    converter = ShuntingYardConverter(premise)
                    converted_premise = converter.convert()
                    converted_premises.append(converted_premise)

                conclusion_converter = ShuntingYardConverter(conclusion)
                converted_conclusion = conclusion_converter.convert()

                # Create an instance of the parser for the first premise to use for checking
                parser = LogicalWFFParser(converted_premises[0])

                is_consequent = parser.check_consequence(converted_premises, converted_conclusion)
                print(
                    f"\nThe premises {'entail' if is_consequent else 'do not entail'} the consequence '{conclusion.strip()}'.")
            except Exception as e:
                print(e)
                print("An error occurred during conversion or entailment checking.")
        else: break
if __name__ == "__main__":
    main()