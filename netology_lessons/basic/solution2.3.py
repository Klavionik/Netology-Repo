"""
ЛЕКЦИЯ 2.3: ЗАДАЧА 1, 2
"""


def main():
    while True:
        print("Введите выражение в Польской нотации\n"
              "Используйте оператор +, -, *, / и два положительных числа\n"
              "Для выхода введите quit\n")
        polish = input()
        if polish == "quit": break
        try:
            operator, operand0, operand1 = polish.strip().split()
            assert operator in "+*-/"
            assert float(operand0) >= 0 and float(operand1) >= 0
            expression = ''.join(operand0 + operator + operand1)
            result = eval(expression)
        except AssertionError:
            print("Не указан оператор или среди операнд есть отрицательное число!\n")
        except ValueError:
            print("Неверное количество аргументов или среди операнд есть текст!\n")
        except ZeroDivisionError:
            print("Вы попытались разделить на ноль и успешно создали сингулярную аномалию. Поздравляем!\n")
        except Exception as error:
            print(f"Что-то пошло не так: {error.args[-1]}")
        else:
            print(result, end="\n\n")


main()
