# LoxErrors.py
# This extends python's built-in error class to include 
# a line number and message for Lox errors.
# This is basically a refactor of the error code in Lox.java. 
# Written by: Joel Peckham.
# Last Modified: 03/16/2022.

class LoxError(Exception):
    def __init__(self, lineNumber, message):
        self.message = message
        self.line = lineNumber
    def __str__(self):
        return f"[line {self.line}] Error: {self.message}"

from Token import TokenType
class TokenError(Exception):
    def __init__(self, token, message):
        self.message = message
        self.token = token
    def __str__(self):
        if self.token.type == TokenType.EOF:
            return f"[line {self.token.line}] Error at end: {self.message}"
        else:
            return f"[line {self.token.line}] Error at '{self.token.lexeme}': {self.message}"

class LoxRuntimeError(Exception):
    def __init__(self, token, message):
        self.message = message
        self.token = token
    def __str__(self):
        return f"{self.message} [line {self.token.line}]"