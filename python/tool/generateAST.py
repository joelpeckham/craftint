# generateAST.py
# This is a tool to generate the AST classes for Lox.
# When run, this script outputs Expr.py and Stmt.py.
# Written by: Joel Peckham.
# Last Modified: 03/16/2022.


class GrammarNotation:
    def __init__(self, notationString):
        self.name = notationString.split(":")[0].strip()
        self.fields = [x.strip().split(" ") for x in notationString.split(":")[1].strip().split(",")]

def defineAST(outputDir, baseClassName, typeList):
    with open(outputDir + baseClassName + ".py", "w") as f:

        # Introduce the file with a comment.
        from datetime import datetime as dt
        startComment = f"""# {baseClassName}.py\n# This file was generated by tool/generateAST.py.\n# Generated by: Joel Peckham.\n# Last Modified: {dt.now()}.\n"""
        f.write(startComment)

        # Import abstract base classes and the Token class.
        f.write("from abc import ABC, abstractmethod\n")
        f.write("from Token import Token\n")

        # Parse the strings in the type list
        typeList = [GrammarNotation(typeString) for typeString in typeList]

        # Write a visitor class containing the visit methods for each type.
        # This visitor class is used to visit each type in the type list.
        # The visit methods are abstract methods.
        f.write("\n")
        f.write(f"class {baseClassName}Visitor(ABC):\n")
        for t in typeList:
            f.write(f"\t@abstractmethod\n")
            f.write(f"\tdef visit{t.name}(self, {t.name}):\n")

defineAST("","Expr", [])