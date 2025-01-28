from itertools import product

from anytree import Node, RenderTree
from copy import deepcopy

def duplicate_node(node):
    new_node = deepcopy(node)
    return new_node

def print_tree(node):
    for pre, _, node in RenderTree(node):
        print(f"{pre}{node.name}")

def get_node_expression(node):
    if node.is_leaf:
        return node.name
    elif node.name == "¬":
        return f"(¬{get_node_expression(node.children[0])})"
    elif node.name in ["∧", "∨"]:
        # Join expressions of all children with the operator symbol
        child_expressions = [get_node_expression(child) for child in node.children]
        return f"({f'{node.name}'.join(child_expressions)})"
    elif node.name in ["⇒", "⇔"]:
        # For binary operators like ⇒ and ⇔, assume exactly two children
        left_expr = get_node_expression(node.children[0])
        right_expr = get_node_expression(node.children[1])
        return f"({left_expr}{node.name}{right_expr})"
    return node.name


def transform_to_nnf(node, indent=0):
    """Transform a formula into Negation Normal Form (NNF) with indented print statements."""
    if node.name == "¬":
        child = node.children[0]

        # Case: Double negation
        if child.name == "¬":
            print("Transformed this formula:")
            print(f"{get_node_expression(node)}")
            print("Into its equivalent:")
            print(f"{get_node_expression(child.children[0])}")
            return transform_to_nnf(child.children[0], indent)

        # Case: Negation of conjunction (De Morgan's Law)
        elif child.name == "∧":
            node_copy = deepcopy(node)
            new_node = Node("∨", parent=node.parent)
            for grandchild in child.children:
                negated_child = Node("¬", parent=new_node)
                negated_child.children = [transform_to_nnf(grandchild, indent + 1)]
            print("Transformed this formula:")
            print(f"{get_node_expression(node_copy)}")
            print("Into its equivalent:")
            print(f"{get_node_expression(new_node)}")
            return transform_to_nnf(new_node, indent)

        # Case: Negation of disjunction (De Morgan's Law)
        elif child.name == "∨":
            node_copy = deepcopy(node)
            new_node = Node("∧", parent=node.parent)
            for grandchild in child.children:
                negated_child = Node("¬", parent=new_node)
                negated_child.children = [transform_to_nnf(grandchild, indent + 1)]
            print("Transformed this formula:")
            print(f"{get_node_expression(node_copy)}")
            print("Into its equivalent:")
            print(f"{get_node_expression(new_node)}")
            return transform_to_nnf(new_node, indent)

        # Case: Negation of implication (Eliminating ⇒)
        elif child.name == "⇒":
            left, right = child.children
            new_node = Node("∧", parent=node.parent)
            negated_right = Node("¬", parent=new_node, children=[transform_to_nnf(duplicate_node(right), indent + 1)])
            new_node.children = [transform_to_nnf(duplicate_node(left), indent + 1), negated_right]
            print("Transformed this formula:")
            print(f"{get_node_expression(node)}")
            print("Into its equivalent:")
            print(f"{get_node_expression(new_node)}")
            return transform_to_nnf(new_node, indent)

        # Case: Negation of equivalence (⇔)
        elif child.name == "⇔":
            left, right = child.children
            left_neg = Node("¬", parent=node.parent, children=[transform_to_nnf(duplicate_node(left), indent + 1)])
            right_neg = Node("¬", parent=node.parent, children=[transform_to_nnf(duplicate_node(right), indent + 1)])
            new_node = Node("∨", parent=node.parent)
            new_node.children = [
                Node("∧", parent=node.parent, children=[transform_to_nnf(duplicate_node(left), indent + 1), right_neg]),
                Node("∧", parent=node.parent, children=[left_neg, transform_to_nnf(duplicate_node(right), indent + 1)]),
            ]
            print("Transformed this formula:")
            print(f"{get_node_expression(node)}")
            print("Into its equivalent:")
            print(f"{get_node_expression(new_node)}")
            return transform_to_nnf(new_node, indent)

        else:
            return duplicate_node(node)

    # Handle implications (⇒)
    elif node.name == "⇒":
        left, right = node.children
        new_node = Node("∨", parent=node.parent)
        negated_left = Node("¬", parent=new_node, children=[transform_to_nnf(duplicate_node(left), indent + 1)])
        new_node.children = [negated_left, transform_to_nnf(duplicate_node(right), indent + 1)]
        print("Transformed this formula:")
        print(f"{get_node_expression(node)}")
        print("Into its equivalent:")
        print(f"{get_node_expression(new_node)}")
        return transform_to_nnf(new_node, indent)

    # Handle equivalences (⇔)
    elif node.name == "⇔":
        left, right = node.children
        left_impl = Node("⇒", parent=node.parent, children=[duplicate_node(left), duplicate_node(right)])
        right_impl = Node("⇒", parent=node.parent, children=[duplicate_node(right), duplicate_node(left)])
        new_node = Node("∧", parent=node.parent, children=[left_impl, right_impl])
        print("Transformed this formula:")
        print(f"{get_node_expression(node)}")
        print("Into its equivalent:")
        print(f"{get_node_expression(new_node)}")
        return transform_to_nnf(new_node, indent)

    # Handle conjunction and disjunction nodes
    elif node.name in ["∧", "∨"]:
        node.children = [transform_to_nnf(child) for child in node.children]

    return simplify_tree(Node(node.name, parent=node.parent, children=node.children))


def transform_to_normal_form(node, conversion_type):
    if conversion_type == "dnf":
        op_list = ["∧", "∨"]
    else:
        op_list = ["∨", "∧"]

    def convert(node):
        if node is None:
            return None
        if node.name == op_list[0]:
            if op_list[1] in [child.name for child in node.children]:
                all_children = [[duplicate_node(grandchild) for grandchild in child.children] if len(child.children) > 1 else [duplicate_node(child)] for child in node.children]
                distributed_children = list(product(*all_children))
                node.name = op_list[1]
                node.children = []
                for children in distributed_children:
                    print(f"Distributed {op_list[0]} over {op_list[1]}:")
                    n = Node(op_list[0], children=[duplicate_node(child) for child in children])
                    print(get_node_expression(n))
                    simplified_n = simplify_tree(deepcopy(n))
                    if get_node_expression(simplified_n) != get_node_expression(n):
                        print("Which simplifies to:")
                        print(get_node_expression(simplified_n))
                    simplified_n.parent = node
                    print("Equivalent formula so far:")
                    print(get_node_expression(simplify_tree(deepcopy(node))))



        for child in node.children[:]:
            convert(child)
        return node

    node = convert(node)
    node = simplify_tree(node)

    return node

def simplify_tree(node):
    if node is None:
        return None  # Early exit if node is None

    # Recursively simplify children
    children_to_remove = []
    for child in node.children[:]:  # Use a copy of the list to allow safe modification
        simplified_child = simplify_tree(child)
        if simplified_child is None:  # If child simplifies to None, mark for removal
            children_to_remove.append(child)

    # Remove any None children
    for child in children_to_remove:
        node.children.remove(child)

    if node.name in {"∨", "∧"}:
        new_children = []
        for child in node.children:
            if child.name == node.name:  # Flatten nested disjunctions/conjunctions
                new_children.extend(child.children)
            else:
                new_children.append(child)
        node.children = new_children

    # Handle specific tautology and contradiction cases
    if node.name == "∨":
        literals = set()
        negations = set()
        for child in node.children:
            if child.name == "¬" and child.children:
                negations.add(child.children[0].name)
            elif child.name:
                literals.add(child.name)

        # Tautology (P ∨ ¬P)
        if literals & negations:
            node.name = "⊤"
            node.children = []
            return node

    elif node.name == "∧":
        literals = set()
        negations = set()
        for child in node.children:
            if child.name == "¬" and child.children:
                negations.add(child.children[0].name)
            elif child.name:
                literals.add(child.name)

        # Contradiction (P ∧ ¬P)
        if literals & negations:
            node.name = "⊥"
            node.children = []
            return node

    # Handle negations of tautologies and contradictions
    if node.name == "¬" and node.children:
        child = node.children[0]
        if child.name == "⊤":
            node.name = "⊥"
            node.children = []
        elif child.name == "⊥":
            node.name = "⊤"
            node.children = []

    # Simplify conjunctions
    elif node.name == "∧":
        new_children = []
        for child in node.children:
            if child.name == "⊤":  # Ignore tautology
                continue
            elif child.name == "⊥":  # Contradiction propagates
                node.name = "⊥"
                node.children = []
                return node
            else:
                new_children.append(child)
        node.children = new_children
        if len(node.children) == 0:
            node.name = "⊤"
            node.children = []
            return node
        if len(node.children) == 1:
            node = node.children[0]

    # Simplify disjunctions
    elif node.name == "∨":
        new_children = []
        for child in node.children:
            if child.name == "⊥":  # Ignore contradiction
                continue
            elif child.name == "⊤":  # Tautology propagates
                node.name = "⊤"
                node.children = []
                return node
            else:
                new_children.append(child)
        node.children = new_children
        if len(node.children) == 0:
            node.name = "⊥"
            node.children = []
            return node
        if len(node.children) == 1:
            node = node.children[0]

    return node
