
"""
ЛЕКЦИЯ 2.4: ЗАДАЧА 1, 2
"""


# TODO 1:
#  Приветствуем пользователя - Запрашиваем название файла с кулинарной книгой - Открываем кулинарную книгу - Передаем
#  объект с книгой функции get_cookbook() - Получаем в ответ словарь со всеми рецептами - Спрашиваем у пользователя нужные блюда
#  и количество персон - Передаем их вместе со словарем рецептов функции get_shoping_list() - Получаем словарь с ингредиентами
#  - Печатаем словарь пользователю и сохраняем его в новый файл
def main():
    while True:
        try:
            print("Добро пожаловать!\nВведите путь к файлу, содержащему кулинарную книгу или quit для выхода")
            cookbook_path = input()
            if cookbook_path == "quit": break
            with open(cookbook_path, encoding="utf8") as cookbook_file:
                cookbook_dict = get_cookbook(cookbook_file)
                print("Кулинарная книга успешно импортирована!")
        except FileNotFoundError:
            print("Указанный файл не найден!\n")
            continue
        except ValueError:
            print("Ошибка импортирования! Проверьте формат кулинарной книги\n")
            continue
        try:
            dishes = input("Введите нужные блюда через запятую\n")
            dishes = [dish.strip().lower() for dish in dishes.split(",")]
            guests = int(input("Введите число гостей\n"))
            if guests < 1: raise ValueError  # Проверяем, чтобы был хотя бы 1 гость
            shopping_dict = get_shopping_list(cookbook_dict, guests, dishes)
        except ValueError:
            print("Число гостей указано неверно!\n")
            continue
        except KeyError:
            print("Такого блюда нет в книге!\n")
            continue
        with open("shopping_list.txt", "w", encoding="utf-8") as shopping_list:
            shopping_list.write("Купить в магазине:\n\n")
            for ingredient, groceries in shopping_dict.items():
                shopping_list.write(f"{ingredient} {groceries['quantity']} {groceries['measure']}\n")
                print(f"{ingredient} {groceries['quantity']} {groceries['measure']}")
        print("Список покупок сохранен в файл shopping_list.txt\n\n")


# TODO 2:
#  Принимаем от main() объект файла книги - Создаем из файла словарь со всеми рецептами - Возвращаем словарь в main()
def get_cookbook(cookbook_file):
    cookbook_dict = {}
    while True:
        dish = cookbook_file.readline().strip()
        if not dish: break
        cookbook_dict[dish] = []
        cookbook_file.readline()
        for line in cookbook_file:
            if line.isspace(): break
            else:
                ingredient_name, quantity, measure = line.split(" | ")
                cookbook_dict[dish].append({"ingredient_name": ingredient_name.strip(),
                                            "quantity": quantity.strip(), "measure": measure.strip()})
    return cookbook_dict


# TODO 3:
#  Принимаем от main() словарь рецептов, количество персон и блюда, генерируем новый словарь с ингредиентами,
#  возвращаем его main()
def get_shopping_list(cookbook, guests, *dishes):
    shopping_dict = {}
    for check_dish in dishes[0]:  # Проверяем, все ли блюда, которые указал юзер, есть в кул. книге
        if check_dish not in [dish_recipe.lower() for dish_recipe in cookbook]: raise KeyError
    for dish in dishes[0]:
        for ingredient in cookbook[dish.capitalize()]:
            name, measure = ingredient["ingredient_name"], ingredient["measure"]
            quantity = int(ingredient["quantity"]) * guests
            shopping_dict.setdefault(name, {})  # Это как-то мало похоже на элегантное решение :(
            shopping_dict[name] = {"measure": measure,
                                   "quantity": quantity + shopping_dict[name].get("quantity", 0)}
    return shopping_dict


main()