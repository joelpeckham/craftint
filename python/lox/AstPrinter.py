# AstPrinter.py
# This is a concrete visitor that prints the AST.
# Written by Joel Peckham.
# Last Modified: 2020-03-17.

from Expr import ExprVisitor
from Stmt import StmtVisitor
from Token import TokenType, Token

class AstPrinter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.indentation = 0
        self.newline = True
        self.outString = ""

    def __str__(self):
        return self.outString
    
    def print(self, element):
        return element.accept(self)
    
    def visitBlock(self, block):
        self.print("{")
        self.indent()
        for statement in block.statements:
            self.print(statement)
        self.dedent()
        self.print("}")
        return self.outString
