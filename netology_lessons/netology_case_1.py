
# Сбор данных для расчета
salary = int(input("Введите заработанную плату в месяц: "))
mortgage_rate = int(input("Введите сколько процентов уходит на ипотеку: "))
expenses_rate = int(input("Введите сколько процентов уходит на жизнь: "))
bonus = int(input("Введите количество премий за год: "))

# Расчет годовой з/п, годовых расходов, суммы оставшейся премии
income = salary * 12
mortgage = mortgage_rate / 100 * income
expenses = expenses_rate / 100 * income
bonus_left = bonus * salary / 2

# Расчет оставшихся в конце года накоплений
savings = income + bonus_left - mortgage - expenses

# Вывод
print("На ипотеку было потрачено: ", mortgage)
print("Было накоплено: ", savings)
