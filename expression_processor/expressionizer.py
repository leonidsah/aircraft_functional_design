from expression_processor.tokenizer import TokenType, Token


# (Token[] -> Expression) processor
class Expressionizer:
    __current = 0

    def __init__(self, tokens):
        self.__tokens = tokens

    def parse_expression(self):
        expr = self.__expression()
        if not self.__is_at_end():
            raise Exception("Expected end of expression, found '" + str(self.__peek().lexeme + "'"))
        return expr

    def __expression(self):
        return self.__assignment()

    def __assignment(self):
        expr = self.__or()
        if self.__match(TokenType.ASSIGN):
            value = self.__assignment()
            if isinstance(expr, VariableExpression):
                name = expr.name
                return AssignExpression(name, value)
            else:
                raise Exception("(__assignment) Invalid assignment target")
        return expr

    def __or(self):
        expr = self.__and()
        while self.__match(TokenType.LOGICAL_OR):
            operator = self.__previous()
            right = self.__and()
            expr = LogicalExpression(expr, operator, right)
        return expr

    def __and(self):
        expr = self.__equality()
        while self.__match(TokenType.LOGICAL_AND):
            operator = self.__previous()
            right = self.__equality()
            expr = LogicalExpression(expr, operator, right)
        return expr

    def __equality(self):
        left = self.__comparison()
        while self.__match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.__previous()
            right = self.__comparison()
            left = BinaryExpression(left, operator, right)
        return left

    def __comparison(self):
        left = self.__addition()
        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.__previous()
            right = self.__addition()
            left = BinaryExpression(left, operator, right)
        return left

    def __addition(self):
        left = self.__multiplication()
        while self.__match(TokenType.PLUS, TokenType.MINUS):
            operator = self.__previous()
            right = self.__multiplication()
            left = BinaryExpression(left, operator, right)
        return left

    def __multiplication(self):
        left = self.__unary()
        while self.__match(TokenType.STAR, TokenType.SLASH, TokenType.MODULO):
            operator = self.__previous()
            right = self.__unary()
            left = BinaryExpression(left, operator, right)
        return left

    def __unary(self):
        if self.__match(TokenType.MINUS):
            operator = self.__previous()
            right = self.__unary()
            return UnaryExpression(operator, right)
        return self.__sqrt()

    def __sqrt(self):
        if self.__match(TokenType.SQUARE_ROOT):
            operator = self.__previous()
            right = self.__unary()
            return UnaryExpression(operator, right)
        return self.__exponent()

    def __exponent(self):
        left = self.__call()
        if self.__match(TokenType.EXPONENT):
            operator = self.__previous()
            right = self.__unary()
            left = BinaryExpression(left, operator, right)
        return left

    def __call(self):
        if self.__matchTwo(TokenType.IDENTIFIER, TokenType.LEFT_PAREN):
            # _ is used as placeholder for temporary or unimportant variable
            name, _ = self.__previousTwo()
            arguments = []
            if (not self.__check(TokenType.RIGHT_PAREN)):
                arguments.append(self.__expression())
                while self.__match(TokenType.COMMA):
                    arguments.append(self.__expression())
            self.__consume(TokenType.RIGHT_PAREN,
                           "(__call) Expected ')' after " + self.__previous().lexeme)
            return CallExpression(name.lexeme, arguments)
        return self.__primary()

    def __primary(self):
        if self.__match(TokenType.NUMBER):
            return LiteralExpression(self.__previous().literal)
        elif self.__match(TokenType.IDENTIFIER):
            return VariableExpression(self.__previous())
        elif self.__match(TokenType.LEFT_PAREN):
            expr = self.__expression()
            self.__consume(TokenType.RIGHT_PAREN,
                           "(__primary) Expected ')' after " + self.__previous().lexeme)
            return GroupingExpression(expr)
        raise Exception("Expected expression after " + self.__previous().lexeme)

    def __match(self, *tokenTypes):
        for type in tokenTypes:
            if (self.__check(type)):
                self.__advance()
                return True
        return False

    def __matchTwo(self, first: TokenType, second: TokenType):
        start = self.__current
        if (self.__match(first) and self.__match(second)):
            return True
        self.__current = start
        return False

    def __check(self, tokenType: TokenType):
        if (self.__is_at_end()):
            return False
        else:
            return self.__peek().type == tokenType

    # Checks current token for TokenType and does advance, otherwise throws exception
    def __consume(self, type: TokenType, message: str):
        if self.__check(type):
            return self.__advance()
        raise Exception("Consume exception with message: " + message)

    def __advance(self):
        if (not self.__is_at_end()):
            self.__current += 1
            return self.__previous()

    def __is_at_end(self):
        return self.__peek().type == TokenType.EOF

    def __peek(self):
        return self.__tokens[self.__current]

    def __previous(self):
        return self.__tokens[self.__current - 1]

    def __previousTwo(self):
        return_val = \
            [self.__tokens[self.__current - 2],
             self.__tokens[self.__current - 1]]
        return return_val


class ExpressionSolver:
    def visit_assign_expr(self, expr) -> float:
        pass

    def visit_logical_expr(self, expr) -> float:
        pass

    def visit_binary_expr(self, expr) -> float:
        pass

    def visit_unary_expr(self, expr) -> float:
        pass

    def visit_call_expr(self, expr) -> float:
        pass

    def visit_literal_expr(self, expr) -> float:
        pass

    def visit_variable_expr(self, expr) -> float:
        pass

    def visit_grouping_expr(self, expr) -> float:
        pass


class Expression:
    def accept(self, visitor: ExpressionSolver) -> float:
        pass

    def __str__(self):
        pass


class AssignExpression(Expression):
    def __init__(self, name: TokenType, value: Expression):
        self.name = name
        self.value = value

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_assign_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                self.name.type.name + ", " +
                self.value.__class__.__name__ + ")")


class LogicalExpression(Expression):
    def __init__(self, left: Expression, operator: TokenType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_logical_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                self.left.__class__.__name__ + ", " +
                self.operator.type.name + ", " +
                self.right.__class__.__name__ + ")")


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: TokenType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_binary_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                self.left.__class__.__name__ + ", " +
                self.operator.type.name + ", " +
                self.right.__class__.__name__ + ")")


class UnaryExpression(Expression):
    def __init__(self, operator: TokenType, right: Expression):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_unary_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                self.operator.type.name + ", " +
                self.right.__class__.__name__ + ")")


class CallExpression(Expression):
    def __init__(self, name: str, arguments):
        self.name = name
        self.arguments = arguments

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_call_expr(self)

    def __str__(self):
        ret_val = (self.__class__.__name__ + ":\t(" +
                   self.left.__class__.__name__ + ", " +
                   self.name + ", (")
        for i in range(len(self.arguments)):
            arg = self.arguments[i]
            ret_val += arg.__class__.__name__
            if i != len(self.arguments) - 1:
                ret_val += ", "
        ret_val += "))"
        return ret_val


class LiteralExpression(Expression):
    def __init__(self, value: float):
        self.value = value

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_literal_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                + str(self.value) + ")")


class VariableExpression(Expression):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_variable_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                + self.name.lexeme + ")")


class GroupingExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: ExpressionSolver):
        return visitor.visit_grouping_expr(self)

    def __str__(self):
        return (self.__class__.__name__ + ":\t(" +
                self.expression.__class__.__name__ + ")")
