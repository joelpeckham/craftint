# LoxInstance.py
# This is an implemenation of instances of Lox classes.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from typing import List
from LoxErrors import LoxRuntimeError
# from LoxClass import LoxClass
from Token import Token

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    
    def get(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.klass.findMethod(name.lexeme)
        if method:
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: object):
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return f"{self.klass.name} instance"
    