from enum import Enum, auto


# (String -> Token[]) processor
class Tokenizer:
    def __init__(self, source):
        self.__source = source
        self.__tokens = []
        self.__start = 0
        self.__current = 0

    def __invalidToken(self, char):
        raise Exception("Invalid token " + str(char))

    def parse_tokens(self):
        while (not self.__is_at_end()):
            self.__scan_token()
        self.__tokens.append(Token(TokenType.EOF, "", None))
        return self.__tokens

    def __is_at_end(self):
        return self.__current >= len(self.__source)

    def __scan_token(self):
        self.__start = self.__current
        c = self.__advance()
        match c:
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '+':
                self.__add_token(TokenType.PLUS)
            case '-':
                self.__add_token(TokenType.MINUS)
            case '*':
                self.__add_token(TokenType.STAR)
            case '/':
                self.__add_token(TokenType.SLASH)
            case '%':
                self.__add_token(TokenType.MODULO)
            case '^':
                self.__add_token(TokenType.EXPONENT)
            case '√':
                self.__add_token(TokenType.SQUARE_ROOT)
            case '=':
                if self.__match('='):
                    self.__add_token(TokenType.EQUAL)
                else:
                    self.__add_token(TokenType.ASSIGN)
            case '!':
                if self.__match('='):
                    self.__add_token(TokenType.NOT_EQUAL)
                else:
                    self.__invalidToken(c)
            case '>':
                if self.__match('='):
                    self.__add_token(TokenType.GREATER_EQUAL)
                else:
                    self.__add_token(TokenType.GREATER)
            case '<':
                if self.__match('='):
                    self.__add_token(TokenType.LESS_EQUAL)
                else:
                    self.__add_token(TokenType.LESS)
            case '|':
                if self.__match('|'):
                    self.__add_token(TokenType.LOGICAL_OR)
                else:
                    self.__invalidToken(c)
            case '&':
                if self.__match('&'):
                    self.__add_token(TokenType.LOGICAL_AND)
                else:
                    self.__invalidToken(c)
            case ',':
                self.__add_token(TokenType.COMMA)
            case '(':
                self.__add_token(TokenType.LEFT_PAREN)
            case ')':
                self.__add_token(TokenType.RIGHT_PAREN)
            case _:
                if self.__is_digit_char(c):
                    self.__number()
                elif self.__is_alpha_char(c):
                    self.__identifier()
                else:
                    self.__invalidToken(c)

    # Определяет, относится ли символ к какому-либо числу
    def __is_digit(self, char, previousChar, nextChar):
        o1 = self.__is_digit_char(char)
        if char == '.':
            o2 = True
        elif char == 'e' or char == 'E':
            o2 = self.__is_digit_char(previousChar) and (
                    self.__is_digit_char(nextChar) or nextChar == '+' or nextChar == '-')
        elif char == '+' or char == '-':
            o2 = (previousChar == 'e' or previousChar == 'E') and self.__is_digit_char(nextChar)
        else:
            o2 = False
        return o1 or o2

    def __number(self):
        while (self.__is_digit_char(self.__peek())):
            self.__advance()
        if (self.__is_digit(self.__peek(), self.__peek_previous(), self.__peek_next())):
            self.__advance()
            while (self.__is_digit(self.__peek(), self.__peek_previous(), self.__peek_next())):
                self.__advance()
        value = float(self.__source[self.__start:self.__current])
        self.__add_token(TokenType.NUMBER, value)

    def __identifier(self):
        while (self.__is_alpha_numeric_char(self.__peek())):
            self.__advance()
        self.__add_token(TokenType.IDENTIFIER)

    def __advance(self):
        index = self.__current
        self.__current += 1
        return self.__source[index]

    def __peek(self):
        if (self.__is_at_end()):
            return "\u0000"
        else:
            return self.__source[self.__current]

    def __peek_previous(self):
        if (self.__current > 0):
            return self.__source[self.__current - 1]
        else:
            return "\u0000"

    def __peek_next(self):
        if (self.__current + 1 >= len(self.__source)):
            return "\u0000"  # Нуль-байт
        else:
            return self.__source[self.__current + 1]

    def __match(self, expected):
        if self.__is_at_end():
            return False
        if self.__source[self.__current] != expected:
            return False
        self.__current += 1
        return True

    def __add_token(self, token_type, literal=None):
        text = self.__source[self.__start:self.__current]
        self.__tokens.append(Token(token_type, text, literal))

    # use .isidentifier()
    def __is_alpha_numeric_char(self, char: str):
        return self.__is_digit_char(char) or self.__is_alpha_char(char)

    # use .isalpha() or == '_'
    def __is_alpha_char(self, char: str):
        return char.isalpha() and len(char) == 1 or char == "_"

    def __is_digit_char(self, char: str):
        return char.isdigit() and len(char) == 1 or char == "."


class Token:
    def __init__(self, type, lexeme, literal):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __str__(self):
        return str("(" + self.type.name) + ", " + self.lexeme + ", " + str(self.literal) + ")"


class TokenType(Enum):
    # Basic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    MODULO = auto()
    EXPONENT = auto()
    SQUARE_ROOT = auto()
    ASSIGN = auto()
    # Logical operators
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    LOGICAL_OR = auto()
    LOGICAL_AND = auto()
    # Other, Note: Comma is used for listing arguments in parentheses
    COMMA = auto()
    # Parentheses
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    # Terminating character
    EOF = auto()


def token_list_to_string(tokens):
    str1 = ""
    for t in tokens:
        str1 += t.lexeme
    return str1


def print_parts(tokens_list_list):
    # Print parts (part of expression is list of tokens)
    print("Parts:")
    i = 0
    for tokens_list in tokens_list_list:
        str1 = ""
        for token in tokens_list:
            str1 += token.__str__() + " "
        print(str(i) + ". " + str1)
        i += 1


def print_tokens(tokens_list):
    # Print parts
    str1 = ""
    for token in tokens_list:
        str1 += token.__str__() + " "
    print("0. " + str1)
