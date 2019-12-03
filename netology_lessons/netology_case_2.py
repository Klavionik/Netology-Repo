
# Сбор данных о призывнике
height = int(input("Введите рост призывника\n"))
age = int(input("Введите возраст призывника\n"))
children = int(input("Количество детей призывника\n"))
student = int(input("Призывник — студент? Введите 1 (да) или 0 (нет)\n"))

# Если мужчина младше 18 или старше 27 лет, имеет двух и более детей
# или учится в вузе, он не подлежит призыву

# Проверка условий и вывод
if (18 <= age <= 27) and (children < 2) and (not student):
    if height <= 165:
        print("Распределить в танковые войска")
    elif 165 < height < 170:
        print("Распределить в ВВС")
    elif 170 <= height <= 190:
        print("Распределить в ВДВ")
    elif height > 190:
        print("Распределить в иные войска")
else: print("Не подлежит призыву")
