from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_FLOOR, ROUND_CEILING
import math

from expression_processor.expressionizer import ExpressionSolver
from expression_processor.expressionizer import Expression
from expression_processor.tokenizer import TokenType


# (Expression -> BigDecimal / Float) processor
class Evaluator(ExpressionSolver):
    def __init__(self):
        self.math_context = getcontext()
        self.math_context.prec = 16
        self.__variables = {}
        self.__functions = {}

    def get_variables(self):
        return self.__variables

    def __define_variable(self, name, value):
        self.__variables[name.lower()] = value

    def define_expr(self, name, expr):
        self.__define_variable(name, self.eval(expr))
        return self

    def add_function(self, name, function):
        self.__functions[name.lower()] = function
        return self

    def eval(self, expr):
        return expr.accept(self)

    def visit_assign_expr(self, expr):
        value = self.eval(expr.value)
        self.__define_variable(expr.name.lexeme, value)
        return value

    def visit_logical_expr(self, expr):
        left = expr.left
        right = expr.right

        if expr.operator.type == TokenType.LOGICAL_OR:
            lv = self.eval(left)
            if (self.is_truthy(lv)):
                return Decimal(1)
            return Decimal(self.is_truthy(self.eval(right)))
        elif expr.operator.type == TokenType.LOGICAL_AND:
            lv = self.eval(left)
            if (not self.is_truthy(lv)):
                return Decimal(0)
            return Decimal(self.is_truthy(self.eval(right)))
        else:
            raise Exception(f"Invalid logical operator '{expr.operator.lexeme}'")

    def visit_binary_expr(self, expr):
        left = self.eval(expr.left)
        right = self.eval(expr.right)

        match expr.operator.type:
            case TokenType.PLUS:
                return Decimal(left) + Decimal(right)
            case TokenType.MINUS:
                return Decimal(left) - Decimal(right)
            case TokenType.STAR:
                return Decimal(left) * Decimal(right)
            case TokenType.SLASH:
                return Decimal(left) / Decimal(right)
            case TokenType.MODULO:
                return Decimal(left) % Decimal(right)
            case TokenType.EXPONENT:
                # Fix bug so float and bigdecimal doesn't work together
                return self.pow(left, right)
            case TokenType.EQUAL:
                return Decimal(left == right)
            case TokenType.NOT_EQUAL:
                return Decimal(left != right)
            case TokenType.GREATER:
                return Decimal(left > right)
            case TokenType.GREATER_EQUAL:
                return Decimal(left >= right)
            case TokenType.LESS:
                return Decimal(left < right)
            case TokenType.LESS_EQUAL:
                return Decimal(left <= right)
            case _:
                raise Exception(f"Invalid binary operator '{expr.operator.lexeme}'")

    def visit_unary_expr(self, expr):
        right = self.eval(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                return -right
            case TokenType.SQUARE_ROOT:
                return math.sqrt(right)
            case _:
                raise Exception("Invalid unary operator")

    def visit_call_expr(self, expr):
        name = expr.name
        function = self.__functions.get(name.lower())
        if function is None:
            raise Exception(f"Undefined function '{name}'")
        # Evaluate every argument then call funciton
        return function.call([self.eval(arg) for arg in expr.arguments])

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_variable_expr(self, expr):
        name = expr.name.lexeme
        value = self.__variables.get(name.lower())
        if value is None:
            raise Exception(f"Undefined variable '{name}'")
        return value

    def visit_grouping_expr(self, expr):
        return self.eval(expr.expression)

    def or_(self, left, right):
        left_val = self.eval(left)
        if self.is_truthy(left_val):
            return Decimal(1)
        return Decimal(self.is_truthy(self.eval(right)))

    def and_(self, left, right):
        left_val = self.eval(left)
        if not self.is_truthy(left_val):
            return Decimal(0)
        return Decimal(self.is_truthy(self.eval(right)))

    def is_truthy(self, value):
        return value != Decimal(0)

    def pow(self, base, exp):
        sign_of_exp = int(exp / abs(exp))
        exp = abs(exp)
        int_part = int(exp)
        frac_part = exp - int_part
        int_pow = base ** int_part
        frac_pow = Decimal(math.pow(float(base), float(frac_part)))
        result = Decimal(int_pow) * frac_pow
        if sign_of_exp == -1:
            result = Decimal(1) / result
        return result


class Function:
    def call(self, arguments):
        pass