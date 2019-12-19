"""
ЛЕКЦИЯ 2.3: Задача 3

Добавлена функция show_persons() (ключ "lp"), выводящая имена всех владельцев документов
"""

documents = [
    {"type": "passport", "number": "2207 876234", "name": "Василий Гупкин"},
    {"type": "invoice", "number": "11-2"},
    {"type": "insurance", "number": "10006", "name": "Аристарх Павлов"}
]

directories = {
        '1': ['2207 876234', '11-2', '5455 028765'],
        '2': ['10006', '5400 028765', '5455 002299'],
        '3': []
      }


def main():  # Главное меню программы. Выбор операции, вызов функции dispatch() с ключом операции
    print("""
    Добро пожаловать! Для начала работы выберите нужную вам операцию, указав ее ключ и нажав Enter\n
    Доступные операции:
    a - добавление нового документа в каталог и в перечень полок
    as - добавление новой полки в перечень
    d - удаление документа из каталога и перечня полок
    l - вывод списка всех имеющихся документов
    lp - вывод списка всех владельцев документов
    m - перемещение документа между полками
    p - поиск владельца документа по номеру документа
    s - поиск номера полки по номеру документа
    quit - выход из программы\n""")
    token = input().strip().lower()
    if token == "quit":
        print("""
    Теперь питание компьютера можно отключить :)""")
        return
    return dispatch(token)


def dispatch(token):  # Проверка ключа операции, вызов функции из словаря (или ошибка и возврат в главное меню)
    tokens = {"a": add_document, "as": add_shelf, "d": delete_document,
              "l": show_documents, "lp": show_persons, "m": move_document,
              "p": person_lookup, "s": shelf_lookup}
    try:
        tokens[token]()
    except (KeyError, ValueError, TypeError):
        print("""
    Введен несуществующий ключ операции или использован неверный формат ввода данных!
    Возврат в главное меню...\n""")
    return main()


def add_document():
    doc_entries = input("""
    Добавление документа в каталог
    Введите через запятую тип документа, номер, имя владельца
    и номер полки, на которую нужно поместить документ\n\n""")
    doc_type, doc_num, owner, shelf = \
        [parameter.strip() for parameter in doc_entries.split(',')]  # Конвертируем строку в лист, лист распаковываем
    while shelf not in directories.keys():
        shelf = input("""
    К сожалению, указанной вами полки не существует
    Введите другой номер полки или menu, чтобы прервать операцию
    и вернуться к списку доступных команд\n\n""").strip().lower()
        if shelf == "menu":
            return main()
    documents.append(dict(type=doc_type, number=doc_num, name=owner))
    directories[shelf].append(doc_num)
    print("""
    Документ успешно добавлен! Возврат в главное меню...\n""")


def add_shelf():
    shelf_num = input("""
    Добавление полки в перечень
    Введите номер полки, под которым она будет добавлена в перечень\n\n""")
    while not shelf_num.isdecimal():
        shelf_num = input("""
    Номер добавляемой полки должен быть целым числом!
    Введите другой номер полки или menu, чтобы прервать операцию
    и вернуться к списку доступных команд\n\n""").strip().lower()
        if shelf_num == "menu":
            return
    if shelf_num not in directories.keys():
        directories[shelf_num] = []
        print(f"""
    Полка №{shelf_num} успешно добавлена! Возврат в главное меню...\n""")
    else:
        print(f"""
    Полка №{shelf_num} уже существует! Возврат в главное меню...\n""")


def delete_document():
    deleted = False
    doc_num = input("""
    Удаление документа
    Введите номер документа, который необходимо удалить\n\n""")
    while not deleted:
        for value, document in enumerate(documents):
            if doc_num in document.values():
                documents.remove(document)
        for shelf_number, directory in list(directories.items()):
            if doc_num in directory:
                directory.remove(doc_num)
                deleted = True
                print(f"""
    Документ {doc_num} успешно удален! Возврат в главное меню...""")
                return
        doc_num = input("""
    Документ не найден! Введите другой номер документа или menu
    чтобы прервать операцию и вернуться к списку доступных команд.\n\n""").strip().lower()
        if doc_num == "menu":
            return


def move_document():
    task_info = input("""
    Перемещение документа
    Введите через запятую номер документа и полку назначения\n\n""")
    doc_num, goal_shelf = \
        [parameter.strip() for parameter in task_info.split(',')]  # Конвертируем строку в лист, лист распаковываем
    while goal_shelf not in directories.keys():
        goal_shelf = input("""
    К сожалению, указанной вами полки не существует
    Введите другой номер полки или menu, чтобы прервать операцию
    и вернуться к списку доступных команд\n\n""").strip().lower()
        if goal_shelf == "menu":
            return main()
    for shelf_number, directory in list(directories.items()):
        if doc_num in directory:
            directory.remove(doc_num)
            directories[goal_shelf].append(doc_num)
            print(f"""
    Документ успешно перемещен на полку №{goal_shelf}! Возврат в главное меню...\n""")
            return
    print("""
    Документ не найден! Возврат в главное меню...\n""")


def shelf_lookup():
    found = False
    doc_num = input("""
    Поиск полки по номеру документа
    Введите номер документа\n\n""")
    while not found:
        for shelf_number, directory in directories.items():
            if doc_num in directory:
                found = True
                print(f"""
    Документ {doc_num} расположен на полке {shelf_number}. Возврат в главное меню...\n""")
                return
        doc_num = input("""
    Документ не найден! Введите другой номер документа или menu
    чтобы прервать операцию и вернуться к списку доступных команд.\n\n""").strip().lower()
        if doc_num == "menu":
            return


def show_documents():
    if len(documents) < 1:
        print("""
    Каталог пуст. Возврат в главное меню...""")
        return
    print("""
    Список документов в каталоге (вид, номер, имя владельца)""")
    for document in documents:
        print(f'''
    {document["type"]}  "{document["number"]}" "{document["name"]}"''', end=' ')
    print("""
    Поиск завершен. Возврат в главное меню...\n""")


def show_persons():
    if len(documents) < 1:
        print("""
    Каталог пуст. Возврат в главное меню...""")
        return
    print("""
    Список владельцев документов в каталоге:""")
    for document in documents:
        try:
            print(f"""
    {document["name"]}""", end=' ')
        except KeyError:
            print(f"""
    Для документа №{document["number"]} не указан владелец!""", end=' ')
    print("""
    Поиск завершен. Возврат в главное меню...\n""")


def person_lookup():
    found = False
    doc_num = input("""
    Поиск владельца по номеру документа
    Введите номер документа\n\n""")
    while not found:
        for document in documents:
            if document["number"] == doc_num:
                found = True
                print(f"""
    Владелец документа №{doc_num}: {document["name"]}. Возврат в главное меню...""")
                return
        doc_num = input("""
    Документ не найден! Введите другой номер документа или menu
    чтобы прервать операцию и вернуться к списку доступных команд.\n\n""").strip().lower()
        if doc_num == "menu":
            return


main()

print(directories)
print(documents)
