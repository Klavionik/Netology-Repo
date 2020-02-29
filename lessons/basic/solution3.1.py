""""
ЛЕКЦИЯ 3.1, ЗАДАЧА 1
"""

import json


# Главное меню, десериализация json-файла, передача объекта
# с json-данными функции find_top10, печать результата работы функции find_top10()
def main():
    print("Поиск топ-10 слов в новостях 'В ОТПУСК.РУ'")
    while True:
        try:
            filename = input("\nВведите имя JSON-файла\n")
            length = int(input("Введите минимальную длину слова\n"))
            with open(filename, encoding="UTF-8") as fhandle:
                json_data = json.load(fhandle)
        except FileNotFoundError:
            print("Файл с указанным именем не найден")
            continue
        except ValueError as error:
            print("Ошибка при работе с данными\nПодробнее:", error)
            continue
        top10 = find_top10(json_data, length)
        print(f"Топ-10 слов от {length} символов в файле {filename}:\n")
        for i, word in enumerate(top10, start=1):
            print(f"{i}. {word}")
        print("\nПоиск завершен")
        break


# Получение объекта с json-данными, поиск и запись в список топ-10
# слов в новостях длиннее length символов, передача списка в main()
def find_top10(json_data, lenght):
    all_words = []
    top10 = []

    for article in json_data["rss"]["channel"]["items"]:
        all_words.extend([word.lower() for word in article["description"].split() if len(word) > lenght])

    for word in sorted(all_words, key=lambda x: all_words.count(x), reverse=True):
        if (word not in top10) and (len(top10) != 10):
            top10.append(word)
    return top10


main()
