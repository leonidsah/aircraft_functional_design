from sklearn import linear_model
import matplotlib.pyplot as plt

from expression_processor.evaluator_wrapper import EvaluatorWrapper
from expression_processor.tokenizer import Token, TokenType, Tokenizer


def open_samples(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.readlines()
        lines = []
        # Ignore lines starting with #
        for line in text:
            if line[0] != '#':
                lines.append(line)
        params_order = lines[0].replace('\n', '').split(',')
        lines.pop(0)
        samples = []
        for line in lines:
            line = [float(x) for x in line.split(',')]
            samples.append(line)
        return [params_order, samples]


def make_plot(predicted_values, observed_values):
    # Создание графика
    plt.figure(figsize=(10, 6))  # Размер графика
    plt.scatter(predicted_values, observed_values, color='blue', label='Observed vs Predicted')

    # Добавление линии y=x для наглядности
    max_val = max(max(predicted_values), max(observed_values))
    plt.plot([0, max_val], [0, max_val], color='red', linestyle='--', label='y=x')

    # Настройка заголовка и подписей осей
    plt.title('Предсказанные и наблюдаемые значения')
    plt.xlabel('Предсказанное значение')
    plt.ylabel('Наблюдаемое значение')
    plt.legend()
    plt.grid(True)

    # Отображение графика
    plt.show()


def substitute_param(param, param_value, param_expression, ew):
    ew.define("AAA", "1")
    ew.define(param, param_value)
    param_expression.append(Token(TokenType.EOF, "", None))
    new_param_value = ew.eval_tokens(param_expression)
    return new_param_value

def fun_mnk(filename, expression):
    return_value = []
    ew = EvaluatorWrapper()
    try:
        samples_obj = open_samples(filename)
    except Exception as e:
        raise Exception(f"Неверный формат файла ({type(e).__name__}: {str(e)})")
    params_order = samples_obj[0][:-1]
    y_param_name = samples_obj[0][-1]

    samples = samples_obj[1]
    x_list = []
    y_list = []
    y_calculated_list = []
    for s in samples:
        x_list.append(s[:-1])
        y_list.append(s[-1])
    res = Main().process_mnk(expression)
    if res is None:
        print("None")
    else:
        print_parts(res)
    # i - place in calculated params
    # j - place in used params
    # if i == j for i in range(len(coefs)) - OK
    # if i != j
    # Определяем как поменять местами параметры и определяем какие-действия нужно выполнить с каждым из параметров
    actions_list = []
    swap_order = []
    for calculated_param_index in range(len(params_order)):
        calculated_param = params_order[calculated_param_index]
        for given_param_index in range(len(res)):
            for token in res[given_param_index]:
                given_param = token.lexeme
                if given_param == calculated_param:
                    swap_order.append([given_param_index, calculated_param_index])
                    print(
                        f"Given param {given_param} is at {given_param_index}, while calculated {calculated_param} is at {calculated_param_index}, so a[{swap_order[-1][0]}] = {params_order[swap_order[-1][1]]}")
                    action = res[given_param_index]
                    for token in action:
                        if token.lexeme == "a" + str(given_param_index):
                            token.lexeme = "AAA"
                    actions_list.append([given_param, action])
    # Высчитавыаем "новую" выборку
    for calculated_param_index in range(len(x_list)):
        for i in range(len(params_order)):
            param = params_order[i]
            param_value = x_list[calculated_param_index][i]
            for i in range(len(actions_list)):
                if param == actions_list[i][0]:
                    param_expression = actions_list[i][1]
                    new_value = float(substitute_param(param, param_value, param_expression, ew))
                    x_list[calculated_param_index][i] = new_value
    # Линейная регрессия
    clf = linear_model.LinearRegression()
    clf.fit(x_list, y_list)
    coefs = clf.coef_
    print("a0, a1, a2 ...:", coefs)
    # Меняем порядок когда уже знаем точные значения параметров; запоминаем порядок изначального выражения
    original_formula_params_order = []
    for i in range(len(params_order)):
        original_formula_params_order.append(0)
        return_value.append(0)
    for swap in swap_order:
        ew.define("a" + str(swap[0]), coefs[swap[1]])
        original_formula_params_order[swap[0]] = params_order[swap[1]]
        return_value[swap[0]] = coefs[swap[1]]
    return_value.append(clf.intercept_)

    # Формула с учетом "вычисленной выборки"
    formula = f"{y_param_name} = "
    for i in range(len(params_order)):
        formula += f"a{i} * {original_formula_params_order[i]}"
        if i != len(params_order) - 1:
            formula += " + "
    print("FORMULA: ", formula)
    # Подставляем значения
    for calculated_param_index in range(len(x_list)):
        for i in range(len(params_order)):
            param = params_order[i]
            param_value = x_list[calculated_param_index][i]
            ew.define(param, param_value)
        answer = float(ew.eval(formula))
        y_calculated_list.append(answer)
    print(f"Predicted:{y_calculated_list[0]}, Observed:{y_list[0]}")
    print("x_list:", x_list)
    print("y_calculated_list:", y_calculated_list)

    y_calculated_list = [y + clf.intercept_ for y in y_calculated_list]
    make_plot(y_calculated_list, y_list)
    return return_value

class Main:
    ew = EvaluatorWrapper()

    def print_formulas(formulas):
        for i in range(len(formulas)):
            print(f"F{i}: '{formulas[i]}'")
        return 0

    def process_formula(self, formula):
        answer = None
        try:
            answer = self.ew.eval(formula)
        except Exception as e:
            print("process_formula exception:" + str(e))
        return answer

    def print_tokens(self, tokens):
        i = 0
        for t in tokens:
            print(str(i) + ". " + str(t))
            i += 1

    def process_mnk(self, formula):
        result = None
        try:
            sc = Tokenizer(formula)
            tokens = sc.parse_tokens()
            # self.print_tokens(tokens)
            result = self.check_for_MNK_formula(tokens)
        except Exception as e:
            raise Exception("process_MNK exception: " + str(e))
        return result

    # Примем, что выражение должно содержать параметры, имеющие название a1, a2, a3, ... и т.д. и никак иначе
    # Нужны коэффициенты при параметрах a1, a2, a3 и свободный коэффициент
    def check_for_MNK_formula(self, tokens):
        count_assign = 0
        params_count = 0
        for t in tokens:
            if t.type == TokenType.ASSIGN:
                count_assign += 1
        # Ensure that formula looks like this:
        # y = ...
        if not ((tokens[0].type == TokenType.IDENTIFIER) and (tokens[1].type == TokenType.ASSIGN) and (
                count_assign == 1)):
            print("Errcode 1")
            return None
        parts = []
        p = []
        for i in range(2, len(tokens)):
            t = tokens[i]
            # print(t.__str__())

            if i == 2 or (t.type != TokenType.PLUS and t.type != TokenType.MINUS):
                p.append(t)
            else:
                parts.append(p)
                p = []
                if t.type == TokenType.MINUS:
                    p.append(t)
        parts.append(p)
        parts[-1] = parts[-1][:-1]  # Удаляем EOF
        # Check parts
        for i in range(len(parts)):
            # Первый токен должен быть идентификатором с именем a0, далее a1, a2 и т.д.
            if parts[i][0].type == TokenType.IDENTIFIER:
                first_identificator = parts[i][0]
            else:
                first_identificator = parts[i][1]
            if first_identificator.type != TokenType.IDENTIFIER:
                raise Exception("Первый токен должен быть идентификатором")
                return None
            if int(first_identificator.lexeme[1]) != i:
                raise Exception("Значения параметров должны соответствовать шаблону a0, a1, a2 и так далее")
                # print("Значения параметров должны соответствовать шаблону a0, a1, a2 и так далее")
                return None
        return parts