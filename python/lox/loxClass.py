# loxClass.py
# This is a implementation of LoxCallable for classes.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from loxCallable import LoxCallable
from typing import List
from LoxErrors import LoxRuntimeError

class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass, methods: List[LoxCallable]):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self):
        return self.name

    def findMethod(self, name: str):
        pass

    