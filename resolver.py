import re
def resolve(clause1, clause2):
    """
    Resolves two clauses and returns the resulting clause(s) if they can be resolved.
    """
    resolved_clauses = []
    for literal in clause1:
        complement = "¬" + literal if not literal.startswith("¬") else literal[1:]
        if complement in clause2:
            new_clause = (clause1 - {literal}) | (clause2 - {complement})
            return [new_clause]
    return []

def unit_propagation(clauses,indentation=""):
    """
    Apply unit propagation to simplify the clauses.
    """
    unit_clauses = [clause for clause in clauses if len(clause) == 1]
    while unit_clauses:
        unit = unit_clauses.pop()
        literal = next(iter(unit))  # Get the single literal
        print(f"{indentation}Found unit literal {literal}")
        complement = "¬" + literal if not literal.startswith("¬") else literal[1:]
        new_clauses = []
        for clause in clauses:
            if literal in clause:
                print(f"{indentation}Removed clause {set(clause)}")
                continue  # Remove clause if literal is found
            if complement in clause:
                new_clause = clause - {complement}
                if len(new_clause) == 0:
                    print(f"{indentation}Removed {complement} from clause {set(clause)} resulting in ∅")
                    return False
                print(f"{indentation}Removed {complement} from clause {set(clause)} resulting {set(new_clause)}")
                if len(new_clause) == 1:
                    unit_clauses.append(new_clause)  # New unit clause found
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)
        if clauses != list(map(frozenset, new_clauses)):
            print(f"{indentation}Clauses after unit propagation:")
            for i in new_clauses:
                print(f"{indentation}{set(i)}")

        clauses = new_clauses
    return clauses

def pure_literal_elimination(clauses,indentation=""):
    """
    Apply pure literal elimination.
    """
    literals = set(literal for clause in clauses for literal in clause)
    pure_literals = set()
    removed = False
    for literal in literals:
        if ('¬' + literal) not in literals and not literal.startswith('¬'):
            pure_literals.add(literal)
        elif literal[1:] not in literals and literal.startswith('¬'):
            pure_literals.add(literal)
    new_clauses = []
    for clause in clauses:
        new_clause = {lit for lit in clause if lit not in pure_literals}
        if new_clause != clause:  # Keep clause if not empty
            print(f"{indentation}Removed clause {set(clause)} because it contains a pure literal")
            removed = True
        else:
            new_clauses.append(new_clause)
    if clauses != list(map(frozenset, new_clauses)):
        print(f"{indentation}Clauses after pure literal elimination:")
        for i in new_clauses:
            print(f"{indentation}{set(i)}")
    if removed:
        new_clauses = pure_literal_elimination(new_clauses)
    return new_clauses

def resolution(clauses, dp=True):
    """
    Determines if the set of clauses is satisfiable using the resolution method.
    Logs each step in the process.
    """
    step = 1
    clauses = [frozenset(clause) for clause in clauses]
    for clause in clauses:
        print(f"({step}) {set(clause)}")
        step += 1
    print()

    while True:
        new = set()
        if not clauses:
            print("\nAnswer: Satisfiable")
            return True
        elif len(clauses) == 0:
            print("\nAnswer: Unsatisfiable")
            return False
        if dp:
            clauses = unit_propagation(clauses)
            if not clauses:
                print("\nAnswer: Unsatisfiable")
                return False
            elif len(clauses) == 0:
                print("\nAnswer: Satisfiable")
                return True
            clauses = pure_literal_elimination(clauses)
            if len(clauses) == 0:
                print("\nAnswer: Satisfiable")
                return True
        clauses = [frozenset(clause) for clause in clauses]
        clauses_set = set(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(len(clauses)) for j in range(i + 1, len(clauses))]
        diff=False
        for (c1, c2) in pairs:
            resolvents = resolve(c1, c2)
            for resolvent in resolvents:
                if not resolvent:  # Empty clause found
                    print(f"({step}) ∅ from {set(c1)} and {set(c2)}")
                    print("\nAnswer: Unsatisfiable")
                    return False
                if frozenset(resolvent) not in clauses_set and not is_tautology(resolvent):
                    print(f"({step}) {set(resolvent)} from {set(c1)} and {set(c2)}")
                    clauses_set.add(frozenset(resolvent))
                    new.add(frozenset(resolvent))
                    step += 1
                # elif frozenset(resolvent) in clauses_set:
                #     print(f"{set(resolvent)} from {set(c1)} and {set(c2)} is already included")
                if new and dp:
                    new_clauses=clauses+list(new)
                    unit_clauses=unit_propagation(new_clauses)
                    if not unit_clauses:
                        print("\nAnswer: Unsatisfiable")
                        return False
                    elif len(unit_clauses) == 0 :
                        print("\nAnswer: Satisfiable")
                        return True
                    pure_clauses=pure_literal_elimination(unit_clauses)
                    if len(pure_clauses) == 0:
                        print("\nAnswer: Satisfiable")
                        return True
                    if new_clauses != pure_clauses:
                        clauses = list(map(frozenset, pure_clauses)) # Updates clauses with the processed clauses
                        diff = True
                        break
            if diff:
                break



        if not new:
            print("\nNo new resolvant to be added ")
            print("Answer: Satisfiable")
            return True

        if not diff:
            clauses.extend(new)

def is_tautology(clause):
    """
    Check if a clause is a tautology (contains both a literal and its negation).
    """
    for literal in clause:
        complement = "¬" + literal if not literal.startswith("¬") else literal[1:]
        if complement in clause:
            return True
    return False


def cnf_tree_to_clauses(node):
    """
        Converts a CNF tree into a list of clauses.
        Each clause is represented as a set of literals.
    """

    if not node.children:
        return [{node.name}]
    clauses = []
    for child in node.children:
        if child.name == '∨':  # If the child represents a disjunction
            clause = set(grab_literals(child))
            clauses.append(clause)
        else:
            clauses.append(grab_literals(child))
    return clauses

def grab_literals(node):
    """
    Recursively collects literals from a disjunction subtree.
    """
    if not node.children:
        return {node.name}
    literals = []
    if node.name == "¬":
        return {f"¬{node.children[0].name}"}
    for child in node.children:
        literals.extend(grab_literals(child))
    return literals


def create_clause_list(string):
    return [] if string == "{}" else [{literal for literal in clause.strip("{}").split(",")} for clause in re.findall(r"{[^{}]*}", string.replace(" ", ""))]


def is_satisfied(assignment, clauses):
    """
    Check if the formula (in terms of clauses) is satisfied given an assignment of truth values.
    """
    for clause in clauses:
        satisfied_clause = False
        for literal in clause:
            # Determine the variable and its negation
            var = literal.lstrip('¬')  # Remove '¬' to get the variable
            negated = (literal != var)  # Check if the literal is negated

            # Check if the literal satisfies the clause
            if var in assignment:
                if negated and not assignment[var]:  # Variable must be False if negated
                    satisfied_clause = True
                    break
                elif not negated and assignment[var]:  # Variable must be True if not negated
                    satisfied_clause = True
                    break
        # If no literal in the clause satisfies, the whole clause is false
        if not satisfied_clause:
            return False
    return True


def backtrack(variables, clauses, assignment):
    """
    Try to find a satisfying assignment using backtracking.
    """
    # If we've assigned values to all variables, check if the formula is satisfied
    if len(assignment) == len(variables):
        if is_satisfied(assignment, clauses):
            return assignment
        else:
            return None

    # Try assigning True to the next unassigned variable
    var = variables[len(assignment)]
    assignment[var] = True
    result = backtrack(variables, clauses, assignment)
    if result is not None:
        return result

    # Backtrack: try assigning False to the next variable
    assignment[var] = False
    result = backtrack(variables, clauses, assignment)
    if result is not None:
        return result

    # If no assignment worked, return None (unsatisfiable)
    del assignment[var]  # Remove the assignment to backtrack
    return None


def find_satisfiable_interpretation(clauses):
    """
    Find a satisfying interpretation for the formula using backtracking.
    """
    # Extract the set of variables from the clauses (positive and negative literals)
    variables = set()
    for clause in clauses:
        for literal in clause:
            # Add the variable without the '¬' symbol
            variables.add(literal.lstrip('¬'))

    # Start the backtracking search with an empty assignment
    assignment = {}
    return backtrack(list(variables), clauses, assignment)

def dpll(clauses, branch=None, indent=0):
    """
    Implements the DPLL algorithm for satisfiability.
    Recursively applies unit propagation, pure literal elimination, and branching.
    """
    indentation = "  " * indent
    clauses = unit_propagation(clauses,indentation)
    if clauses is False:
        if branch:
            print(f"{indentation}Answer: Unsatisfiable (after unit propagation) for {branch} branch")
        else:
            print(f"{indentation}Answer: Unsatisfiable (after unit propagation)")
        return False
    elif not clauses:
        if branch:
            print(f"Answer: Satisfiable (after unit propagation) for {branch} branch")
        else:
            print(f"{indentation}Answer: Satisfiable (after unit propagation)")
        return True

    clauses = pure_literal_elimination(clauses)
    if not clauses:
        if branch:
            print(f"{indentation}Answer: Satisfiable (after pure literal elimination) for {branch} branch")
        else:
            print(f"{indentation}Answer: Satisfiable (after pure literal elimination)")
        return True

    literal = next(iter(clauses[0]))

    # Create two branches: one where the literal is true and one where the literal is false
    clauses_true = [frozenset(clause) for clause in clauses]
    clauses_false = [frozenset(clause) for clause in clauses]

    # Add the literal to the true branch and the negation of the literal to the false branch
    negation= "¬" + literal if not literal.startswith("¬") else literal[1:]
    clauses_true.append(frozenset([literal]))
    clauses_false.append(frozenset([negation]))

    # Recursively solve the true branch
    print(f"\n{indentation}Branching on {literal} = True")
    if dpll(clauses_true,literal, indent + 1):
        print(f"{indentation}Answer: Satisfiable with {literal} = True")
        return True

    # Recursively solve the false branch
    print(f"\n{indentation}Branching on {literal} = False")
    if dpll(clauses_false, negation, indent + 1):
        print(f"{indentation}Answer: Satisfiable with {literal} = False")
        return True

    # If neither branch is satisfiable, the formula is unsatisfiable
    print(f"{indentation}Answer: Unsatisfiable (both branches failed for {literal})")
    return False
