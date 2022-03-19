# Resolver.py
# This class is a concrete visitor that resolves the AST.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

import Expr as E
import Stmt as S
from Token import Token
from Environment import Environment
from Interpreter import Interpreter
from LoxCallable import LoxCallable
from LoxErrors import LoxRuntimeError
from collections import deque
from enum import Enum, auto
from typing import List, Deque, Dict

class FunctionType(Enum):
    NONE = auto()
    METHOD = auto()
    INITIALIZER = auto()
    FUNCTION = auto()
    GETTER = auto()
    SETTER = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

class Resolver(E.ExprVisitor, S.StmtVisitor):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: Deque[Dict[str, bool]] = deque()
        self.currentFunction = FunctionType.NONE
        self.currentClass = ClassType.NONE
    
    def resolve(self, statements):
        if not isinstance(statements, List):
            statements = [statements]
        for statement in statements:
            statement.accept(self)
    
    def beginScope(self):
        self.scopes.append({})

    def endScope(self):
        self.scopes.pop()
    
    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise LoxRuntimeError(name, "Variable with this name already declared in this scope.")
        scope[name.lexeme] = False
    
    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True
    
    def resolveLocal(self, expr: E.Expr, name: Token):
        i = len(self.scopes) - 1
        while i >= 0:
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i);
                return
            i -= 1

    def visitBlockStmt(self, block: S.Block):
        self.beginScope()
        self.resolve(block.statements)
        self.endScope()
    
    def visitClassStmt(self, classStmt: S.Class):
        enclosingClass: ClassType = self.currentClass
        self.currentClass = ClassType.CLASS

        self.declare(classStmt.name)
        self.define(classStmt.name)

        if classStmt.superclass and classStmt.superclass.name.lexeme == classStmt.name.lexeme:
            raise LoxRuntimeError(classStmt.name, "A class cannot inherit from itself.")
        
        if classStmt.superclass:
            self.currentClass = ClassType.SUBCLASS
            self.resolve(classStmt.superclass)
        
        if classStmt.superclass:
            self.beginScope()
            self.scopes[-1]["super"] = True
        
        self.beginScope()
        self.scopes[-1]["this"] = True

        for method in classStmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolveFunction(method, declaration)
        
        self.endScope()

        if classStmt.superclass:
            self.endScope()
        
        self.currentClass = enclosingClass

    def visitExpressionStmt(self, stmt: S.Expression):
        self.resolve(stmt.expression)
    
    def visitFunctionStmt(self, stmt: S.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt, FunctionType.FUNCTION)
    
    def visitIfStmt(self, stmt: S.If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch:
            self.resolve(stmt.elseBranch)
    
    def visitPrintStmt(self, stmt: S.Print):
        self.resolve(stmt.expression)
    
    def visitReturnStmt(self, stmt: S.Return):
        if self.currentFunction == FunctionType.NONE:
            raise LoxRuntimeError(stmt.keyword, "Cannot return from top-level code.")
        if stmt.value:
            if self.currentFunction == FunctionType.INITIALIZER:
                raise LoxRuntimeError(stmt.keyword, "Cannot return a value from an initializer.")
            self.resolve(stmt.value)
    
    def visitVarStmt(self, stmt: S.Var):
        self.declare(stmt.name)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
    
    def visitWhileStmt(self, stmt: S.While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
    
    def visitAssignExpr(self, expr: E.Assign):
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)
    
    def visitBinaryExpr(self, expr: E.Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitCallExpr(self, expr: E.Call):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)
        
    def visitGetExpr(self, expr: E.Get):
        self.resolve(expr.object)

    def visitGroupingExpr(self, expr: E.Grouping):
        self.resolve(expr.expression)
    
    def visitLiteralExpr(self, expr: E.Literal):
        return None
    
    def visitLogicalExpr(self, expr: E.Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)
    
    def visitSetExpr(self, expr: E.Set):
        self.resolve(expr.value)
        self.resolve(expr.object)
    
    def visitSuperExpr(self, expr: E.Super):
        if self.currentClass == ClassType.NONE:
            raise LoxRuntimeError(expr.keyword, "Cannot use 'super' outside of a class.")
        if self.currentClass == ClassType.CLASS:
            raise LoxRuntimeError(expr.keyword, "Cannot use 'super' in a class with no superclass.")
        self.resolveLocal(expr, expr.keyword)
    
    def visitThisExpr(self, expr: E.This):
        if self.currentClass == ClassType.NONE:
            raise LoxRuntimeError(expr.keyword, "Cannot use 'this' outside of a class.")
        self.resolveLocal(expr, expr.keyword)
    
    def visitUnaryExpr(self, expr: E.Unary):
        self.resolve(expr.right)
    
    def visitVariableExpr(self, expr: E.Variable):
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme, None) == False:
            raise LoxRuntimeError(expr.name, "Cannot read local variable in its own initializer.")
        self.resolveLocal(expr, expr.name)
        
    def resolveFunction(self, function: S.Function, funcType: FunctionType):
        enclosingFunction: FunctionType = self.currentFunction
        self.currentFunction = funcType
        
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve(function.body)
        self.endScope()
        
        self.currentFunction = enclosingFunction
    
    