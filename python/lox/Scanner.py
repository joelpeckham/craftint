from Token import Token, TokenType
class Scanner:
    def __init__(self, source: str):

        self._keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE
        }

        self._source = source
        self._tokens = []
        self._start = 0
        self._current = 0
        self._line = 1
    

    def isAtEnd(self):
        return self._current >= len(self._source)
    
    def isDigit(self, c):
        return c.isdigit()

    def isAlpha(self, c):
        return c.isalpha() or c == "_"

    def isAlphaNum(self, c):
        return self.isAlpha(c) or self.isDigit(c)
    
    def addToken(self, tokenType: TokenType, literal = None):
        text = self._source[self._start:self._current]
        self._tokens.append(Token(tokenType, text, literal, self._line))

    def advance(self):
        self._current += 1
        return self._source[self._current - 1]
    
    def peek(self):
        if self.isAtEnd():
            return "\0"
        return self._source[self._current]
    
    def peekNext(self):
        if self._current + 1 >= len(self._source):
            return "\0"
        return self._source[self._current + 1]
    
    def match(self, expected: str):
        if self.isAtEnd():
            return False
        if self._source[self._current] != expected:
            return False
        self._current += 1
        return True
    
    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == "\n":
                self._line += 1
            self.advance()
        if self.isAtEnd():
            print("Unterminated string.")
            return None
        self.advance()
        self.addToken(TokenType.STRING, self._source[self._start + 1:self._current - 1])
    
    def number(self):
        while self.isDigit(self.peek()):
            self.advance()
        if self.peek() == "." and self.isDigit(self.peekNext()):
            self.advance()
            while self.isDigit(self.peek()):
                self.advance()
        self.addToken(TokenType.NUMBER, float(self._source[self._start:self._current]))

    def identifier(self):
        while self.isAlphaNum(self.peek()):
            self.advance()
        text = self._source[self._start:self._current]
        identifierType = self._keywords.get(text)
        if identifierType is None:
            identifierType = TokenType.IDENTIFIER
        self.addToken(identifierType)
    
    def scanToken(self):
        c = self.advance()
        if c == '(':
            self.addToken(TokenType.LEFT_PAREN)
        elif c == ')':
            self.addToken(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.addToken(TokenType.LEFT_BRACE)
        elif c == '}':
            self.addToken(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.addToken(TokenType.COMMA)
        elif c == '.':
            self.addToken(TokenType.DOT)
        elif c == '-':
            self.addToken(TokenType.MINUS)
        elif c == '+':
            self.addToken(TokenType.PLUS)
        elif c == ';':
            self.addToken(TokenType.SEMICOLON)
        elif c == '*':
            self.addToken(TokenType.STAR)
        elif c == '!':
            if self.match("="):
                self.addToken(TokenType.BANG_EQUAL)
            else:
                self.addToken(TokenType.BANG)
        elif c == '=':
            if self.match("="):
                self.addToken(TokenType.EQUAL_EQUAL)
            else:
                self.addToken(TokenType.EQUAL)
        elif c == '<':
            if self.match("="):
                self.addToken(TokenType.LESS_EQUAL)
            else:
                self.addToken(TokenType.LESS)
        elif c == '>':
            if self.match("="):
                self.addToken(TokenType.GREATER_EQUAL)
            else:
                self.addToken(TokenType.GREATER)
        elif c == '/':
            if self.match("/"):
                while self.peek() != "\n" and not self.isAtEnd():
                    self.advance()
            else:
                self.addToken(TokenType.SLASH)
        elif c == ' ' or c == '\r' or c == '\t':
            pass
        elif c == '\n':
            self._line += 1
        elif c == '"':
            self.string()
        else:
            if self.isDigit(c):
                self.number()
            elif self.isAlpha(c):
                self.identifier()
            else:
                print("Unexpected character.")
        
    def scanTokens(self):
        while not self.isAtEnd():
            self._start = self._current
            self.scanToken()
        self.addToken(TokenType.EOF, "", None, self._line)
        return self._tokens