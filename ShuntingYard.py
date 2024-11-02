import re


class ShuntingYardConverter:
    def __init__(self, expression):
        self.expression = expression.replace(" ", "")
        self.output_queue = []
        self.operator_stack = []

        # Define operator precedence and associativity
        self.precedence = {
            '¬': 3,  # Unary NOT
            '∧': 2,  # AND
            '∨': 2,  # OR
            '⇒': 1,  # IMPLIES
            '⇔': 0  # EQUIVALENT
        }
        self.right_associative = {'¬'}

    def is_operator(self, token):
        return token in self.precedence

    def precedence_of(self, token):
        return self.precedence.get(token, 0)

    def convert(self):
        # Tokenize the input
        tokens = re.findall(r"[A-Z][0-9]*|¬|∧|∨|⇒|⇔|[()]", self.expression)

        for token in tokens:
            if re.match(r"[A-Z][0-9]*", token):  # Atomic proposition
                self.output_queue.append(token)
            elif token == '(':
                self.operator_stack.append(token)
            elif token == ')':
                while self.operator_stack and self.operator_stack[-1] != '(':
                    self.output_queue.append(self.operator_stack.pop())
                self.operator_stack.pop()  # Remove '('
            elif self.is_operator(token):
                while (self.operator_stack and self.operator_stack[-1] != '(' and
                       (self.precedence_of(self.operator_stack[-1]) > self.precedence_of(token) or
                        (self.precedence_of(self.operator_stack[-1]) == self.precedence_of(token) and
                         token not in self.right_associative))):
                    self.output_queue.append(self.operator_stack.pop())
                self.operator_stack.append(token)

        # Pop all remaining operators to output queue
        while self.operator_stack:
            self.output_queue.append(self.operator_stack.pop())

        # Return the converted expression in strict syntax
        return self.construct_expression_from_postfix()

    def construct_expression_from_postfix(self):
        stack = []

        for token in self.output_queue:
            print(f"Queue: {self.output_queue}")
            if token in self.precedence:
                pattern = re.escape(token)
                if token == '¬':  # Unary operation
                    operand = stack.pop()
                    expression = f"(¬{operand})"
                else:  # Binary operation
                    right = stack.pop()
                    left = stack.pop()
                    if re.search(pattern, left) is not None:
                       new_left=re.sub(r"[()]","",left)
                       print(new_left)
                       expression = f"({new_left} {token} {right})"
                    else : expression = f"({left} {token} {right})"
                stack.append(expression)
            else:
                stack.append(token)
            print(stack)

        return stack[0]



# Example usage:
expressions = [
    "P ∧ (Q ⇒ R)",
    "¬(P ∧ Q)",
    "P ∧ Q ∧ R",
    "¬(P ∨ Q)",
    "P ⇒ Q ⇔ R"
]

for expr in expressions:
    converter = ShuntingYardConverter(expr)
    strict_syntax = converter.convert()
    print(f"Original: {expr}\nConverted: {strict_syntax}\n")