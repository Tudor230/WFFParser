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

def unit_propagation(clauses):
    """
    Apply unit propagation to simplify the clauses.
    """
    unit_clauses = [clause for clause in clauses if len(clause) == 1]
    while unit_clauses:
        unit = unit_clauses.pop()
        literal = next(iter(unit))  # Get the single literal
        print(f"Found unit literal {literal}")
        complement = "¬" + literal if not literal.startswith("¬") else literal[1:]
        new_clauses = []
        for clause in clauses:
            if literal in clause:
                print(f"Removed clause {set(clause)}")
                continue  # Remove clause if literal is found
            if complement in clause:
                new_clause = clause - {complement}
                if len(new_clause) == 0:
                    print(f"Removed {complement} from clause {set(clause)} resulting in ∅")
                    return []
                print(f"Removed {complement} from clause {set(clause)} resulting {set(new_clause)}")
                if len(new_clause) == 1:
                    unit_clauses.append(new_clause)  # New unit clause found
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)
        if clauses != list(map(frozenset, new_clauses)):
            print("Clauses after unit propagation:")
            for i in new_clauses:
                print(set(i))

        clauses = new_clauses
    return clauses

def pure_literal_elimination(clauses):
    """
    Apply pure literal elimination.
    """
    literals = set(literal for clause in clauses for literal in clause)
    pure_literals = set()
    for literal in literals:
        if ('¬' + literal) not in literals and not literal.startswith('¬'):
            pure_literals.add(literal)
        elif literal[1:] not in literals and literal.startswith('¬'):
            pure_literals.add(literal)
    new_clauses = []
    for clause in clauses:
        new_clause = {lit for lit in clause if lit not in pure_literals}
        if new_clause != clause:  # Keep clause if not empty
            print(f"Removed clause {set(clause)} because it contains a pure literal")
        else:
            new_clauses.append(new_clause)
    if clauses != list(map(frozenset, new_clauses)):
        print("Clauses after pure literal elimination:")
        for i in new_clauses:
            print(set(i))
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
        if dp:
            clauses = unit_propagation(clauses)
            clauses = pure_literal_elimination(clauses)
        if not clauses:
            print("\nAnswer: Unsatisfiable")
            return False

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
                    new.add(frozenset(resolvent))
                    step += 1
                if new and dp:
                    new_clauses=clauses+list(new)
                    new_clauses=unit_propagation(new_clauses)
                    if len(new_clauses) == 0 :
                        print("\nAnswer: Unsatisfiable")
                        return False
                    new_clauses=pure_literal_elimination(new_clauses)
                    if len(new_clauses) == 0 :
                        print("\nAnswer: Unsatisfiable")
                        return False
                    clauses = list(map(frozenset, new_clauses))
                    diff = True
                    break
            if diff:
                break



        if not new:
            print("\nNo new resolvant ")
            print("Answer: Satisfiable")
            return True

def is_tautology(clause):
    """
    Check if a clause is a tautology (contains both a literal and its negation).
    """
    for literal in clause:
        complement = "¬" + literal if not literal.startswith("¬") else literal[1:]
        if complement in clause:
            return True
    return False


# Input clauses
# clauses = [
#     {"F1", "¬F2"},  # (F1 ∨ ¬F2)
#     {"F1", "F3"},  # (F1 ∨ F3)
#     {"¬F2", "F3"},  # (¬F2 ∨ F3)
#     {"¬F1", "F2"},  # (¬F1 ∨ F2)
#     {"F2", "¬F3"},  # (F2 ∨ ¬F3)
#     {"¬F1", "¬F3"},  # (¬F1 ∨ ¬F3)
# ]

# clauses = [
#     {"F1", "F2"},     # (F1 ∨ F2)
#     {"¬F1", "F3"},    # (¬F1 ∨ F3)
#     {"¬F2", "¬F3"},   # (¬F2 ∨ ¬F3)
#     {"F1", "¬F3"},    # (F1 ∨ ¬F3)
# ]

# clauses = [
#     {"¬A", "¬W", "P"},   # (¬A ∨ ¬W ∨ P)
#     {"A", "I"},          # (A ∨ I)
#     {"W", "M"},          # (W ∨ M)
#     {"¬P"},              # (¬P)
#     {"¬E", "¬I"},        # (¬E ∨ ¬I)
#     {"¬E", "¬M"},        # (¬E ∨ ¬M)
#     {"¬E"},               # (E)
# ]

clauses = [
    {"P", "Q", "¬R"},    # (P ∨ Q ∨ ¬R)
    {"¬P", "R"},         # (¬P ∨ R)
    {"P", "¬Q", "S"},    # (P ∨ ¬Q ∨ S)
    {"¬P", "¬Q", "¬R"},  # (¬P ∨ ¬Q ∨ ¬R)
    {"P", "¬S"},         # (P ∨ ¬S)
]


# Check satisfiability
resolution(clauses, dp=True)
