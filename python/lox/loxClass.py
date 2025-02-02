# loxClass.py
# This is a implementation of LoxCallable for classes.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from LoxCallable import LoxCallable
from typing import List
from LoxFunction import LoxFunction
from LoxInstance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass, methods: List[LoxCallable]):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self):
        return self.name

    def findMethod(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.findMethod(name)
        return None
    
    def call(self, interpreter, arguments: List[object]) -> object:
        instance = LoxInstance(self)
        initializer = self.findMethod("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer = self.findMethod("init")
        if initializer:
            return initializer.arity()
        return 0