# This is a Python adaption of the following Kotlin project: https://github.com/Keelar/ExprK
# Это адаптация на языке Python следующего проекта: ExprK (https://github.com/Keelar/ExprK)
# author: leonidsah
import math
from decimal import ROUND_FLOOR, ROUND_CEILING, Decimal

from expression_processor.evaluator import Evaluator, Function
from expression_processor.expressionizer import Expressionizer
from expression_processor.tokenizer import Tokenizer


class EvaluatorWrapper:
    def __init__(self):
        self.__evaluator = Evaluator()
        self.define("pi", math.pi)
        self.define("e", math.e)
        self.__evaluator.add_function("abs", AbsFunction())
        self.__evaluator.add_function("sum", SumFunction())
        self.__evaluator.add_function("floor", FloorFunction())
        self.__evaluator.add_function("ceil", CeilFunction())
        self.__evaluator.add_function("round", RoundFunction())
        self.__evaluator.add_function("min", MinFunction())
        self.__evaluator.add_function("max", MaxFunction())
        self.__evaluator.add_function("sqrt", SqrtFunction())

        self.precision = self.__evaluator.math_context.prec
        self.roundingMode = self.__evaluator.math_context.rounding

    def set_precision(self, precision):
        self.__evaluator.math_context.prec = precision
        return self

    def set_rounding_mode(self, rounding_mode):
        self.__evaluator.math_context.rounding = rounding_mode
        return self

    def define(self, name: str, expression: str):
        expr = self.__parse_string_to_expression(str(expression))
        self.__evaluator.define_expr(name, expr)
        return self

    def add_function(self, name: str, func: Function):
        self.__evaluator.add_function(name, func)

    def eval(self, expression: str) -> Decimal:
        return self.__evaluator.eval(self.__parse_string_to_expression(expression))

    def eval_tokens(self, tokens):
        return self.__evaluator.eval(self.__parse_tokens_to_expression(tokens))

    def eval_to_string(self, expression):
        try:
            result = self.__evaluator.eval(self.__parse_string_to_expression(expression))
            return str(result.normalize())
        except Exception as e:
            return str(e)

    def eval_expression(self, expression):
        try:
            result = self.__evaluator.eval(expression)
            return str(result.normalize())
        except Exception as e:
            print("eval_expression exception: " + str(e))
            return None

    def __parse_string_to_expression(self, string):
        return Expressionizer(Tokenizer(string).parse_tokens()).parse_expression()

    def __parse_tokens_to_expression(self, tokens):
        return Expressionizer(tokens).parse_expression()

    def __parse_string_to_tokens(self, expression: str):
        return Tokenizer(expression).parse_tokens()

    def get_variables(self):
        return self.__evaluator.get_variables()

    def print_variables(self):
        for k, v in self.get_variables().items():
            print(f"{k} = {v}")


class AbsFunction(Function):
    def call(self, arguments):
        if len(arguments) != 1:
            raise Exception("abs requires one argument")
        return abs(arguments[0])


class SumFunction(Function):
    def call(self, arguments):
        if not arguments:
            raise Exception("sum requires at least one argument")
        return sum(arguments)


class FloorFunction(Function):
    def call(self, arguments):
        if len(arguments) != 1:
            raise Exception("floor requires one argument")
        return arguments[0].to_integral_exact(rounding=ROUND_FLOOR)


class CeilFunction(Function):
    def call(self, arguments):
        if len(arguments) != 1:
            raise Exception("ceil requires one argument")
        return arguments[0].to_integral_exact(rounding=ROUND_CEILING)


class RoundFunction(Function):
    def call(self, arguments):
        if len(arguments) not in {1, 2}:
            raise Exception("round requires either one or two arguments")
        value = arguments[0]
        scale = arguments[1] if len(arguments) == 2 else 0
        return value.quantize(Decimal('1e-{0}'.format(scale)))


class MinFunction(Function):
    def call(self, arguments):
        if not arguments:
            raise Exception("min requires at least one argument")
        return min(arguments)


class MaxFunction(Function):
    def call(self, arguments):
        if not arguments:
            raise Exception("max requires at least one argument")
        return max(arguments)


class SqrtFunction(Function):
    def call(self, arguments):
        if len(arguments) != 1:
            raise Exception("sqrt requires only one argument")
        return math.sqrt(arguments[0])
