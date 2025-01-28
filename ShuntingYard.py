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
        print(f"Converting the expression: {self.expression}")
        tokens = re.findall(r"[A-Z][0-9]*|¬|∧|∨|⇒|⇔|[()]|⊤|⊥", self.expression)
        for token in tokens:
            print(f"Processing token: {token}")
            if re.match(r"[A-Z][0-9]*|⊤|⊥", token):  # Atomic proposition
                print(f"Token is atomic proposition, adding to output queue: {token}")
                self.output_queue.append(token)
            elif token == '(':
                print("Token is '(', adding to operator stack")
                self.operator_stack.append(token)
            elif token == ')':
                print("Token is ')', popping operators until '('")
                while self.operator_stack and self.operator_stack[-1] != '(':
                    self.output_queue.append(self.operator_stack.pop())
                print("Popping '(' from operator stack")
                self.operator_stack.pop()  # Remove '('
            elif self.is_operator(token):
                print(f"Token is operator '{token}', checking precedence and associativity")
                while (self.operator_stack and self.operator_stack[-1] != '(' and
                       (self.precedence_of(self.operator_stack[-1]) > self.precedence_of(token) or
                        (self.precedence_of(self.operator_stack[-1]) == self.precedence_of(token) and
                         token not in self.right_associative))):
                    popped = self.operator_stack.pop()
                    print(f"Popping operator {popped} to output queue due to precedence/associativity")
                    self.output_queue.append(popped)
                print(f"Adding operator '{token}' to operator stack")
                self.operator_stack.append(token)

        print("Popping remaining operators from operator stack to output queue")
        while self.operator_stack:
            popped = self.operator_stack.pop()
            print(f"Popping operator {popped} to output queue")
            self.output_queue.append(popped)

        # Return the converted expression in strict syntax
        print(f"Output queue after conversion: {self.output_queue}")
        return self.construct_expression_from_postfix()

    def construct_expression_from_postfix(self):
        print("Constructing expression from postfix notation")
        stack = []

        for token in self.output_queue:
            print(f"Processing token: {token}")
            if token in self.precedence:
                if token == '¬':  # Unary operation
                    operand = stack.pop()
                    print(f"Unary operator '¬' with operand {operand}")
                    expression = f"(¬{operand})"
                else:  # Binary operation
                    right = stack.pop()
                    left = stack.pop()
                    # if token in {'∨', '∧'} and re.search(re.escape(token), left) is not None:
                    #    new_left=left[1:-1]
                    #    expression = f"({new_left}{token}{right})"
                    print(f"Binary operator '{token}' with operands {left} and {right}")
                    expression = f"({left}{token}{right})"
                stack.append(expression)
                print(f"Pushed expression to stack: {expression}")
            else:
                stack.append(token)
                print(f"Pushed atomic proposition to stack: {token}")
        if len(stack) != 1:
            raise Exception("Error converting from relaxed syntax to strong syntax")

        print(f"Final converted expression: {stack[0]}")

        return stack[0]


