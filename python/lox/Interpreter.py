# Interpreter.py
# This class is a concrete visitor that interprets the AST.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from numpy import isin
import Expr as E
import Stmt as S
from Token import Token, TokenType
from Environment import Environment
from LoxCallable import LoxCallable
from time import time
from typing import List
from LoxErrors import LoxRuntimeError
from LoxClass import LoxClass
from LoxFunction import LoxFunction
from Return import Return
from LoxInstance import LoxInstance

class ClockCallable(LoxCallable):
    def arity(self) -> int:
        return 0
    def call(self, interpreter, arguments):
        return time()
    def __str__(self):
        return "<native fn>"

class Interpreter(E.ExprVisitor, S.StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

        self.globals.define("clock", ClockCallable())
    
    def interpret(self, statements: List[S.Stmt]):
        try:
            for statement in statements:
                statement.accept(self)
        except LoxRuntimeError as e:
            raise e

    def resolve(self, expr: E.Expr, depth: int):
        self.locals[expr] = depth
    
    def executeBlock(self, statements: List[S.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                statement.accept(self)
        finally:
            self.environment = previous
    
    def visitBlockStmt(self, block: S.Block):
        self.executeBlock(block.statements, Environment(self.environment))
    
    def visitClassStmt(self, classStmt: S.Class):
        superclass = None
        if classStmt.superclass:
            superclass = classStmt.superclass.accept(self)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(classStmt.superclass.name, "Superclass must be a class.")
        
        self.environment.define(classStmt.name.lexeme, None)

        if classStmt.superclass:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        
        methods = {}
        for method in classStmt.methods:
            func = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = func
        
        klass = LoxClass(classStmt.name.lexeme, superclass, methods)
        if classStmt.superclass:
            self.environment = self.environment.enclosing
        self.environment.assign(classStmt.name, klass)

    def visitExpressionStmt(self, stmt: S.Expression):
        stmt.expression.accept(self)
    
    def visitFunctionStmt(self, function: S.Function):
        func = LoxFunction(function, self.environment, False)
        self.environment.define(function.name.lexeme, func)
    
    def isTruthy(self, obj) -> bool:
        if obj == None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def visitIfStmt(self, stmt: S.If):
        if self.isTruthy(stmt.condition.accept(self)):
            stmt.thenBranch.accept(self)
        elif stmt.elseBranch:
            stmt.elseBranch.accept(self)
    
    def stringify(self, obj) -> str:
        if obj == None:
            return "nil"
        if isinstance(obj, str):
            return obj
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, float):
            if obj == int(obj):
                if obj == 0:
                    if str(obj).startswith("-"):
                        return "-0"
                    else:
                        return "0"
                return str(int(obj))
            else:
                return str(obj)
        return str(obj)

    def visitPrintStmt(self, stmt: S.Print):
        value = stmt.expression.accept(self)
        print(self.stringify(value))
    
    def visitReturnStmt(self, stmt: Return):
        value = None
        if stmt.value:
            value = stmt.value.accept(self)
        raise Return(value)
    
    def visitVarStmt(self, stmt: S.Var):
        value = None
        if stmt.initializer:
            value = stmt.initializer.accept(self)
        self.environment.define(stmt.name.lexeme, value)
    
    def visitWhileStmt(self, stmt: S.While):
        while self.isTruthy(stmt.condition.accept(self)):
            stmt.body.accept(self)
    
    def visitAssignExpr(self, expr: E.Assign):
        value = expr.value.accept(self)
        distance = self.locals.get(expr, None)
        if distance != None:
            self.environment.assignAt(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def isEqual(self, a, b) -> bool:
        if a == None and b == None:
            return True
        if a == None:
            return False
        if type(a) != type(b):
            return False
        return a == b
    
    def checkNumberOperand(self, operator: Token, operand):
        if not isinstance(operand, (int, float)):
            raise LoxRuntimeError(operator, "Operand must be a number.")
    
    def checkNumberOperands(self, operator: Token, left, right):
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise LoxRuntimeError(operator, "Operands must be numbers.")
    
    def visitBinaryExpr(self, expr: E.Binary):
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        opType = expr.operator.type

        if opType == TokenType.BANG_EQUAL:
            return not self.isEqual(left, right)
        if opType == TokenType.EQUAL_EQUAL:
            return self.isEqual(left, right)
        if opType == TokenType.GREATER:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) > float(right)
        if opType == TokenType.GREATER_EQUAL:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) >= float(right)
        if opType == TokenType.LESS:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) < float(right)
        if opType == TokenType.LESS_EQUAL:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) <= float(right)
        if opType == TokenType.MINUS:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) - float(right)
        if opType == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        if opType == TokenType.SLASH:
            self.checkNumberOperands(expr.operator, left, right)
            if right == 0:
                return float('nan')
            return float(left) / float(right)
        if opType == TokenType.STAR:
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) * float(right)
    
    def visitCallExpr(self, expr: E.Call):
        callee = expr.callee.accept(self)
        arguments = []
        for argument in expr.arguments:
            arguments.append(argument.accept(self))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.parent, "Can only call functions and classes.")
        
        func = callee
        if len(arguments) != func.arity():
            raise LoxRuntimeError(expr.parent, "Expected " + str(func.arity()) + " arguments but got " + str(len(arguments)) + ".")
        return func.call(self, arguments)
    
    def visitGetExpr(self, expr: E.Get):
        obj = expr.object.accept(self)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")
    
    def visitGroupingExpr(self, expr: E.Grouping):
        return expr.expression.accept(self)
    
    def visitLiteralExpr(self, expr: E.Literal):
        return expr.value
    
    def visitLogicalExpr(self, expr: E.Logical):
        left = expr.left.accept(self)
        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left):
                return left
        else:
            if not self.isTruthy(left):
                return left
        return expr.right.accept(self)
    
    def visitSetExpr(self, expr: E.Set):
        obj = expr.object.accept(self)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value = expr.value.accept(self)
        obj.set(expr.name, value)
        return value
    
    def visitSuperExpr(self, expr: E.Super):
        distance = self.locals.get(expr, None)
        superclass = self.environment.getAt(distance, "super")
        obj = self.environment.getAt(distance-1, "this")
        method = superclass.findMethod(expr.method.lexeme)
        if method == None:
            raise LoxRuntimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")
        return method.bind(obj)
    
    def lookUpVariable(self, name: Token, expr : E.Expr):
        distance = self.locals.get(expr, None)
        if distance != None:
            return self.environment.getAt(distance, name.lexeme)
        return self.globals.get(name)

    def visitThisExpr(self, expr: E.This):
        return self.lookUpVariable(expr.keyword, expr)
    
    def visitUnaryExpr(self, expr: E.Unary):
        right = expr.right.accept(self)
        if expr.operator.type == TokenType.BANG:
            return not self.isTruthy(right)
        if expr.operator.type == TokenType.MINUS:
            self.checkNumberOperand(expr.operator, right)
            return -float(right)
        return None
    
    def visitVariableExpr(self, expr: E.Variable):
        return self.lookUpVariable(expr.name, expr)

