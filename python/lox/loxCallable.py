# loxCallable.py
# This is an interface for callable objects.
# Written by Joel Peckham.
# Last Modified: 2020-03-18.

from abc import ABC, abstractmethod

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list) -> object:
        pass
    
    @abstractmethod
    def arity(self) -> int:
        pass
    