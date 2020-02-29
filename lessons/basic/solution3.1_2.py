""""
ЛЕКЦИЯ 3.1, ЗАДАЧА 2
"""

import xml.etree.ElementTree as ET


# Главное меню, десериализация xml-файла, передача объекта
# с xml-данными функции find_top10, печать результата работы функции find_top10()
def main():
    print("Поиск топ-10 слов в новостях 'В ОТПУСК.РУ'")
    while True:
        try:
            filename = input("\nВведите имя XML-файла\n")
            length = int(input("Введите минимальную длину слова\n"))
            with open(filename, encoding="UTF-8") as fhandle:
                xml_data = ET.parse(fhandle)
        except FileNotFoundError:
            print("Файл с указанным именем не найден")
            continue
        except ValueError as error:
            print("Ошибка при работе с данными\nПодробнее:", error)
            continue
        top10 = find_top10(xml_data, length)
        print(f"Топ-10 слов от {length} символов в файле {filename}:\n")
        for i, word in enumerate(top10, start=1):
            print(f"{i}. {word}")
        print("\nПоиск завершен")
        break


# Получение объекта с xml-данными, поиск и запись в список топ-10
# слов в новостях длиннее length символов, передача списка в main()
def find_top10(xml_data, lenght):
    all_words = []
    top10 = []

    for element in xml_data.findall("channel/item/description"):
        all_words.extend([word.lower() for word in element.text.split() if len(word) > lenght])

    for word in sorted(all_words, key=lambda x: all_words.count(x), reverse=True):
        if (word not in top10) and (len(top10) != 10):
            top10.append(word)

    return top10


main()
