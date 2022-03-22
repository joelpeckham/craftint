# LoxFunction.py 
# This is a implementation of LoxCallable for functions.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from LoxCallable import LoxCallable
import Stmt as S
from Environment import Environment
from LoxInstance import LoxInstance
from Return import Return

class LoxFunction(LoxCallable):
    def __init__(self, declaration: S.Function, closure: Environment, isInitializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer

    def bind(self, instance: LoxInstance):
        env = Environment(self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.isInitializer)
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def call(self, interpreter, arguments: list) -> object:
        env = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            env.define(param.lexeme, arg)
        try:
            interpreter.executeBlock(self.declaration.body, env)
        except Return as ret:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return ret.value
        
        if self.isInitializer:
            return self.closure.getAt(0, "this")
        return None
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


