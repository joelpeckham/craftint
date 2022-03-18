# Interpreter.py
# This class is a concrete visitor that interprets the AST.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

import Expr as E
import Stmt as S
from Token import Token
from Environment import Environment
from loxCallable import LoxCallable
from time import time
from typing import List
from LoxErrors import LoxRuntimeError

class ClockCallable(LoxCallable):
    def arity(self) -> int:
        return 0
    def call(self, interpreter, arguments):
        return time()
    def __str__(self):
        return "<native fn> (clock)"

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
            superclass = self.evaluate(classStmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(classStmt.superclass.name,
                                      "Superclass must be a class.")
        self.environment.define(classStmt.name.lexeme, None)
        if classStmt.superclass:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods = {}
        for method in classStmt.methods:
            method.accept(self)
            methods[method.name.lexeme] = self.locals[method]
        self.environment = self.environment.enclosing
        self.environment.assign(classStmt.name, LoxClass(classStmt.name.lexeme,
                                                         superclass,
                                                         methods))