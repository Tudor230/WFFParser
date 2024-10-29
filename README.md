
---

<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">WFFPARSER</h1></p>
<p align="center">
	<em><code>❯ A Python-based parser for Well-Formed Formulas (WFF) in propositional logic.</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/Tudor230/WFFParser?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/Tudor230/WFFParser?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/Tudor230/WFFParser?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/Tudor230/WFFParser?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

The **WFFParser** is a Python-based parser designed to analyze and evaluate well-formed formulas (WFF) in propositional logic. It utilizes a tree structure to represent logical expressions, enabling straightforward evaluation and validation.

---

##  Features

- **Parsing Logic**: Parses logical expressions, including unary (¬) and binary (∧, ∨, ⇒, ⇔) operations.
- **Tree Representation**: Represents parsed expressions as a tree, allowing for easy traversal and evaluation.
- **Validity Checking**: Determines if the given logical formula is valid, satisfiable, or unsatisfiable.
- **Truth Table Generation**: Generates a truth table for the evaluated formula.
- **User-Friendly Output**: Provides clear console outputs during parsing and evaluation to assist users in understanding the process.

---

##  Project Structure

```sh
└── WFFParser/
    ├── LICENSE
    └── wff.py
```
---

##  Getting Started

###  Prerequisites

Before getting started with WFFParser, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python 3.x
- **Dependencies:** `anytree`, `itertools`

###  Installation

Install WFFParser using one of the following methods:

**Build from source:**

1. Clone the WFFParser repository:
   ```sh
   ❯ git clone https://github.com/Tudor230/WFFParser
   ```

2. Navigate to the project directory:
   ```sh
   ❯ cd WFFParser
   ```

3. Install the project dependencies (use pip):
   ```sh
   ❯ pip install anytree
   ```

###  Usage
To run the WFFParser, you will need to use the provided for loop within the code to test various propositions. The for loop is structured to parse a list of logical formulas and evaluate them. Here is how you can do it:

1. Open the `wff.py` file.
2. Locate the following section in the code:
    ```python
    # Testing with propositions
    propositions = [
        "(¬(P ∧ Q))",
        "(¬P ∨ (Q ∧ R))",
        ...
    ]

    values = [
        {"P": True, "Q": False},
        {"P": True, "Q": True}
    ]

    for prop in propositions:
        parser = LogicalWFFParser(prop)
        ...
    ```
3. Modify the `propositions` list to include your own logical formulas.
4. You can also modify the `values` list to change the truth assignments for the variables in your propositions.
5. Run the script to see the results of the parsing and evaluations.


---


##  License

This project is protected under the [MIT License](https://choosealicense.com/licenses/mit). For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- Thanks to the developers of `anytree` for providing a robust tree structure implementation.

--- 
