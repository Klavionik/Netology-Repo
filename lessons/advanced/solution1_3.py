"""
LESSON 1.3: EX. 1, 2
"""


# EX. 1
class Contact:

    def __init__(self, name, surname, number, favourite=False, **kwargs):
        self.name, self.surname = name, surname
        self.number = number
        self.favourite = favourite
        self.extra_info = kwargs

    def __str__(self):
        extras = str()
        if self.extra_info:
            for key, value in self.extra_info.items():
                extras += f"\t{key} : {value}\n"
        else:
            extras = "не указана\n"
        return f"""Имя: {self.name}\nФамилия: {self.surname}\nТелефон: {self.number}\nВ избранных: {
                 'да' if self.favourite else 'нет'}\nДополнительная информация:\n{extras}"""


# EX. 2
class PhoneBook:

    def __init__(self, name, *args):
        self.name = name
        self.contacts = list()
        if args:
            for arg in args:
                self.contacts.append(arg)

    def add_contact(self, *args):
        for arg in args:
            self.contacts.append(arg)

    def delete(self, number):
        to_delete = None

        for contact in self.contacts:
            if contact.number == number:
                to_delete = contact

        if to_delete:
            self.contacts.remove(to_delete)
            print(f"Контакт с номером {number} успешно удален\n")
        else:
            print("Контакт с таким номером телефона не найден\n")

    def favourite_numbers(self):
        favourites = list()

        for contact in self.contacts:
            if contact.favourite:
                favourites.append(contact.number)

        if favourites:
            print("Номера в избранном:")
            for number in favourites:
                print(number)
        else:
            print("Номера в избранном отсутствуют\n")

    def find_contact(self, name, surname):
        found = list()

        for contact in self.contacts:
            if contact.name == name and contact.surname == surname:
                found.append(contact)

        if found:
            print("Найденные контакты:")
            for contact in found:
                print(contact)
        else:
            print("Контакт с таким именем и фамилией не найден\n")

    def show_contacts(self):
        print(f"Контакты в телефонной книге {self.name}:")
        for contact in self.contacts:
            print(contact)


if __name__ == '__main__':

    # создание контактов
    mrdoe = Contact("John", "Doe", "+79001111111", email="john.d@gmail.com")
    msdoe = Contact("Jane", "Doe", "+79002222222", True, email="jane.d@gmail.com", instagram="@jane")

    # создание телефонной книги
    my_pb = PhoneBook("Roman's Phone Book", mrdoe, msdoe)

    # создание новых контактов
    agentsmith = Contact("Elrond", "Smith", "+7985427452", True)
    neo = Contact("Thomas", "Anderson", "+097431232323", nickname="The One")

    # добавление новых контактов в телефонную книгу
    my_pb.add_contact(neo, agentsmith)

    # вывод контактов из телефонной книги
    my_pb.show_contacts()

    # удаление контакта из телефонной книги по номеру
    my_pb.delete("+79001111111")

    # поиск контакта в телефонной книге по имени и фамилии
    my_pb.find_contact("Thomas", "Anderson")

    # вывод всех избранных номеров
    my_pb.favourite_numbers()



