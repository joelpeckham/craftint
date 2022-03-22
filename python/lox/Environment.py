# Environment.py
# This class represents the environment in which the Lox interpreter runs.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from LoxErrors import TokenError
from Token import Token

class Environment():
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
    
    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)
        raise TokenError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def assign(self, name: Token, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise TokenError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def define(self, name: str, value):
        self.values[name] = value
    
    def ancestor(self, distance: int):
        if self.enclosing and distance > 0:
            return self.enclosing.ancestor(distance - 1)
        return self
    
    def getAt(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)
    
    def assignAt(self, distance: int, name: Token, value):
        self.ancestor(distance).values[name.lexeme] = value
    
    def __str__(self) -> str:
        return str(self.values) + " -> " + str(self.enclosing) if self.enclosing else ""
    
    