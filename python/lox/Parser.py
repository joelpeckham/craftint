# Parser.py
# Written by: Joel Peckham.
# Last Modified: 2022-03-17.

from Token import TokenType, Token
from LoxErrors import TokenError
from typing import List
import Expr
import Stmt
import sys

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
    
    def isAtEnd(self):
        return self.peek().type == TokenType.EOF
    
    def advance(self):
        self.current += 1
        return self.tokens[self.current - 1]
    
    def check(self, tokenType):
        if self.isAtEnd():
            return False
        return self.peek().type == tokenType
    
    def consume(self, tokenType, message):
        if self.check(tokenType):
            return self.advance()
        raise TokenError(self.peek(), message)
    
    def match(self, tokenTypes: List[TokenType]):
        for tokenType in tokenTypes:
            if self.check(tokenType):
                self.advance()
                return True
        return False
    
    def synchronize(self):
        self.advance()
        while not self.isAtEnd():

            returnIfPrevious = [TokenType.SEMICOLON]
            returnIfNext = [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]

            if self.previous().type in returnIfPrevious:
                return
            if self.peek().type in returnIfNext:
                return
            self.advance()

    def parse(self):
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        return statements

    def expression(self) -> Expr.Expr:
        return self.assignment()

    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match([TokenType.CLASS]):
                return self.classDeclaration()
            if self.match([TokenType.FUN]):
                return self.function("function")
            if self.match([TokenType.VAR]):
                return self.varDeclaration()
            return self.statement()
        except TokenError as e:
            print(e, file=sys.stderr)
            self.synchronize()
            return None
    
    def classDeclaration(self) -> Stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.match([TokenType.LESS]):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Expr.Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Stmt.Class(name, superclass, methods)
    
    def statement(self) -> Stmt.Stmt:
        if self.match([TokenType.FOR]):
            return self.forStatement()
        if self.match([TokenType.IF]):
            return self.ifStatement()
        if self.match([TokenType.PRINT]):
            return self.printStatement()
        if self.match([TokenType.RETURN]):
            return self.returnStatement()
        if self.match([TokenType.WHILE]):
            return self.whileStatement()
        if self.match([TokenType.LEFT_BRACE]):
            return Stmt.Block(self.block())
        return self.expressionStatement()
    
    def forStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()
        if increment is not None:
            body = Stmt.Block([body, Stmt.Expression(increment)])
        if condition is None:
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)
        if initializer is not None:
            body = Stmt.Block([initializer, body])
        return body
    
    def ifStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        thenBranch = self.statement()
        elseBranch = None
        if self.match([TokenType.ELSE]):
            elseBranch = self.statement()
        return Stmt.If(condition, thenBranch, elseBranch)
    
    def printStatement(self) -> Stmt.Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def returnStatement(self) -> Stmt.Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Stmt.Return(keyword, value)
    
    def varDeclaration(self) -> Stmt.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)
    
    def whileStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return Stmt.While(condition, body)
    
    def expressionStatement(self) -> Stmt.Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)
    
    def function(self, kind: str) -> Stmt.Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            do = True
            while do:
                if len(parameters) >= 255:
                    raise TokenError(self.peek(), "Cannot have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match([TokenType.COMMA]):
                    do = False
        self.consume(TokenType.RIGHT_PAREN, f"Expect ')' after {kind} parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Stmt.Function(name, parameters, body)
    
    def block(self) -> List[Stmt.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def assignment(self) -> Expr.Expr:
        expr = self.or_()
        if self.match([TokenType.EQUAL]):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)
            elif isinstance(expr, Expr.Get):
                return Expr.Set(expr.object, expr.name, value)

            raise TokenError(equals, "Invalid assignment target.")
        return expr

    def or_(self) -> Expr.Expr:
        expr = self.and_()
        while self.match([TokenType.OR]):
            operator = self.previous()
            right = self.and_()
            expr = Expr.Logical(expr, operator, right)
        return expr
    
    def and_(self) -> Expr.Expr:
        expr = self.equality()
        while self.match([TokenType.AND]):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)
        return expr
    
    def equality(self) -> Expr.Expr:
        expr = self.comparison()
        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        return expr
    
    def comparison(self) -> Expr.Expr:
        expr = self.term()
        while self.match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)
        return expr
    
    def term(self) -> Expr.Expr:
        expr = self.factor()
        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr.Expr:
        expr = self.unary()
        while self.match([TokenType.SLASH, TokenType.STAR]):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)
        return expr
    
    def unary(self) -> Expr.Expr:
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        return self.call()
    
    def call(self) -> Expr.Expr:
        expr = self.primary()
        while True:
            if self.match([TokenType.LEFT_PAREN]):
                expr = self.finishCall(expr)
            elif self.match([TokenType.DOT]):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Expr.Get(expr, name)
            else:
                break
        return expr
    
    def finishCall(self, callee: Expr.Expr) -> Expr.Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            do = True
            while do:
                if len(arguments) >= 255:
                    raise TokenError(self.peek(), "Cannot have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match([TokenType.COMMA]):
                    do = False
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Expr.Call(callee, paren, arguments)

    def primary(self) -> Expr.Expr:
        if self.match([TokenType.FALSE]):
            return Expr.Literal(False)
        if self.match([TokenType.TRUE]):
            return Expr.Literal(True)
        if self.match([TokenType.NIL]):
            return Expr.Literal(None)
        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return Expr.Literal(self.previous().literal)
        if self.match([TokenType.SUPER]):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Expr.Super(keyword, method)
        if self.match([TokenType.THIS]):
            return Expr.This(self.previous())
        if self.match([TokenType.IDENTIFIER]):
            return Expr.Variable(self.previous())
        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)
        raise TokenError(self.peek(), "Expect expression.")
    
