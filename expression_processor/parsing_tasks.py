from expression_processor.expressionizer import BinaryExpression, Expressionizer
from expression_processor.tokenizer import TokenType, Tokenizer

constraint_tokentypes_list = [TokenType.LESS,
                              TokenType.LESS_EQUAL,
                              TokenType.GREATER,
                              TokenType.GREATER_EQUAL,
                              TokenType.EQUAL,
                              TokenType.NOT_EQUAL,
                              TokenType.LOGICAL_OR,
                              TokenType.LOGICAL_AND]


def all_tokens_in_list(tokens, tokentypes_list):
    for t in tokens:
        if t.type not in tokentypes_list:
            return False
    return True


def any_tokens_in_list(tokens, tokentypes_list):
    for t in tokens:
        if t.type in tokentypes_list:
            return True
    return False


def check_for_expr(expr, expected_expr_type, tokentypes_list):
    if not isinstance(expr, expected_expr_type):
        return False
    if expr.operator.type in tokentypes_list:
        return True
    else:
        return False


def check_for_constraint(expression):
    tokens = Tokenizer(expression).parse_tokens()
    expr = Expressionizer(tokens).parse_expression()
    return check_for_expr(expr, BinaryExpression, constraint_tokentypes_list)
