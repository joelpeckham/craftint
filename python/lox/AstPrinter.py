# AstPrinter.py
# This is a concrete visitor that prints the AST.
# Written by Joel Peckham.
# Last Modified: 2020-03-17.

from Expr import ExprVisitor
from Stmt import StmtVisitor

class AstPrinter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.outString = ""

    def __str__(self):
        return self.outString
    
    def print(self, element):
        return element.accept(self)

    def parenthesize(self, name, elementList):
        s = f"({name}"
        for expression in elementList:
            s += " " + self.print(expression)
        s += ")"
        return s

    # def parenthesizeParts(self, name, partList):
    #     s = f"({name}"
    #     s += self.transformParts(partList)
    #     s += ")"
    #     return s
    
    # def transformParts(self, partList):
    #     pass
    def visitBlockStmt(self, block):
        s = "(block "
        for stmt in block.statements:
            s += self.print(stmt)
        s += ")"
        return s
    
    def visitClassStmt(self, classStmt):
        s = "(class " + classStmt.name.lexeme + " "
        if classStmt.superclass:
            s += " < " + self.print(classStmt.superclass)
        for method in classStmt.methods:
            s += self.print(method)
        s += ")"
        return s
    
    def visitExpressionStmt(self, expressionStmt):
        return self.parenthesize(";", [expressionStmt.expression])

    def visitFunctionStmt(self, functionStmt):
        s = "(fun " + functionStmt.name.lexeme + "("
        for param in functionStmt.params:
            if param != functionStmt.params[0]:
                s += " "
            s += param.lexeme
        s += ") "
        for stmt in functionStmt.body:
            s += self.print(stmt)
        s += ")"
        return s
    
    def visitIfStmt(self, ifStmt):
        if ifStmt.elseBranch:
            return self.parenthesize("if-else", [ifStmt.condition, ifStmt.thenBranch, ifStmt.elseBranch])
        else:
            return self.parenthesize("if", [ifStmt.condition, ifStmt.thenBranch])
    
    def visitPrintStmt(self, printStmt):
        return self.parenthesize("print", [printStmt.expression])
    
    def visitReturnStmt(self, returnStmt):
        return self.parenthesize("return", [returnStmt.value])

    def visitVarStmt(self, varStmt):
        if varStmt.initializer:
            return self.parenthesize("var", [varStmt.name, varStmt.initializer])
        else:
            return self.parenthesize("var", [varStmt.name])
    
    def visitWhileStmt(self, whileStmt):
        return self.parenthesize("while", [whileStmt.condition, whileStmt.body])
    
    def visitAssignExpr(self, assignExpr):
        return self.parenthesize("=", [assignExpr.name.lexeme, assignExpr.value])
    
    def visitBinaryExpr(self, binaryExpr):
        return self.parenthesize(binaryExpr.operator.lexeme, [binaryExpr.left, binaryExpr.right])
    
    def visitCallExpr(self, callExpr):
        return self.parenthesize("call", [callExpr.callee, *callExpr.args])
    
    def visitGetExpr(self, getExpr):
        return self.parenthesize(".", [getExpr.object, getExpr.name])
    
    def visitGroupingExpr(self, groupingExpr):
        return self.parenthesize("group", [groupingExpr.expression])
    
    def visitLiteralExpr(self, literalExpr):
        if literalExpr.value == None:
            return "nil"
        else:
            return str(literalExpr.value)
        
    def visitLogicalExpr(self, logicalExpr):
        return self.parenthesize(logicalExpr.operator.lexeme, [logicalExpr.left, logicalExpr.right])

    def visitSetExpr(self, setExpr):
        return self.parenthesize("=", [setExpr.object, setExpr.name.lexeme, setExpr.value])
    
    def visitSuperExpr(self, superExpr):
        return self.parenthesize("super", [superExpr.method])
    
    def visitThisExpr(self, thisExpr):
        return "this"
    
    def visitUnaryExpr(self, unaryExpr):
        return self.parenthesize(unaryExpr.operator.lexeme, [unaryExpr.right])
    
    def visitVariableExpr(self, variableExpr):
        return variableExpr.name.lexeme

    