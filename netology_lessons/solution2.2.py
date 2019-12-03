from random import randrange, choice
from pprint import pprint

"""
ЛЕКЦИЯ 2.2

Как устроена ферма?

Мы просыпаемся утром, здороваемся с животными, кормим их, доим, собираем яйца, стрижем, выводим гулять, 
после прогулки опять кормим, укладываем спать. 
За ночь животные накапливают ресурс (яйца, молоко, шерсть), и завтра все сначала.

Кормление увеличивает вес животных на случайный процент от 1 до 5.

"""
# TODO 1:
#  Нужно реализовать классы животных, не забывая использовать наследование,
#  определить общие методы взаимодействия с животными и дополнить их в дочерних классах, если потребуется.
#  У каждого животного должно быть определено имя(self.name) и вес(self.weight) (задача 3).


class Cattle:
    title = "Домашний скот"
    hunger = True
    position = "дома"
    says = ''
    resource = True
    _animals_weight = {}

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
        self._animals_weight[self.name] = weight

    def feed(self):
        if self.hunger:
            self.hunger = False
            self.weight += self.weight / 100 * randrange(1, 6)
            self._animals_weight[self.name] = round(self.weight, 2)
            print("Животное {} накормлено и прибавило в весе".format(self.name))
        else:
            print("Животное {} не голодно. Попробуйте выгулять его".format(self.name))

    def pasture(self):
        self.position = "гуляет"
        print("{} {}".format(self.name, self.position))

    def come_back(self, reason="уже темнеет"):
        self.position = "Дома"
        self.hunger = True
        print("Животное {} вернулось домой, причина: {}".format(self.name, reason))

    def morning(self, question):
        print(question)
        print("{} {} {}".format(self.title, self.name, self.says))

    def sleep(self):
        self.resource = True
        self.hunger = True
        print("Доброй ночи, {}!".format(self.name))

    @classmethod
    def show_cattle(cls):
        return cls._animals_weight

    @classmethod
    def get_weight(cls):
        total_weight = 0
        for name in cls._animals_weight:
            total_weight += cls._animals_weight[name]
        return round(total_weight, 2)


class Goose(Cattle):
    title = "Гусь"
    says = "шипит"

    def collect_eggs(self):
        if self.resource:
            self.resource = False
            print("{} {}: собрано {} яиц".format(self.title, self.name, randrange(8)))
        else:
            print("Дай животным поспать!")


class Cow(Cattle):
    title = "Корова"
    says = "мычит"

    def milk(self):
        if self.resource:
            self.resource = False
            print("Корова {} подоена, получено {} л молока".format(self.name, randrange(8, 15)))
        else:
            print("Дай животным поспать!")


class Duck(Cattle):
    title = "Утка"
    says = "крякает"

    def collect_eggs(self):
        if self.resource:
            self.resource = False
            print("{} {}: собрано {} яиц".format(self.title, self.name, randrange(8)))
        else:
            print("Дай животным поспать!")


class Chicken(Cattle):
    title = "Курица"
    says = "кудахчет"

    def collect_eggs(self):
        if self.resource:
            self.resource = False
            print("{} {}: собрано {} яиц".format(self.title, self.name, randrange(8)))
        else:
            print("Дай животным поспать!")


class Sheep(Cattle):
    title = "Овца"
    says = "блеет"

    def shear(self):
        if self.resource:
            self.resource = False
            print("Овца {} подстрижена, получено {} кг шерсти".format(self.name, randrange(5, 15)))
        else:
            print("Дай животным поспать!")


class Shegoat(Cattle):
    title = "Коза"
    says = "блеет по-козлиному"

    def milk(self):
        if self.resource:
            self.resource = False
            print("Коза {} подоена, получено {} л молока".format(self.name, randrange(1, 3)))
        else:
            print("Дай животным поспать!")


# TODO 2, 3:
#  Для каждого животного из списка должен существовать экземпляр класса.
#  Каждое животное требуется накормить и подоить/постричь/собрать яйца, если надо.
#  Необходимо посчитать общий вес всех животных(экземпляров класса);
#  Вывести название самого тяжелого животного.


# Создаем объекты животных с именем и весом каждого
cow = Cow("Манька", 750)
goose0, goose1 = Goose("Серый", 3), Goose("Белый", 4)
duck = Duck("Кряква", 1.3)
chicken0, chicken1 = Chicken("Ко-ко", 0.8), Chicken("Кукареку", 0.76)
shegoat = Shegoat("Егоза", 100)
sheep0, sheep1 = Sheep("Кудрявый", 67), Sheep("Барашек", 70)

# Получаем список животных, чтобы в этом убедиться
pprint(Cattle.show_cattle(), indent=0, compact=True)
print()

# Список причин пораньше вернуться в стойло для коровы :)
reasons = ("закусали мухи", "пошел град", "рога отвалились")


# Вход в программу
def main():
    days = int(input("Сколько дней проведем на ферме?\n"))
    fast_forward(days)
    print("Вот и все, пора домой. Пока, Дядюшка Джо!")


# Проматываем симуляцию фермы на n дней вперед (генерирует много вывода!)
def fast_forward(days):
    while days:
        print("Доброе утро! Осталось дней на ферме: {}\n\n".format(days))
        # Общаемся с животными
        cow.morning("Как дела, Манька?")
        goose0.morning("Как жизнь, Серый?"), goose1.morning("Как настроение, Белый?")
        duck.morning("Как спалось, Кряква?")
        chicken0.morning("Хорошая погодка, да, Ко-ко?"), chicken1.morning("Как здоровье, Кукареку?")
        shegoat.morning("Сегодня не будешь бодаться, Егоза?")
        sheep0.morning("Подстрижем тебя сегодня, Кудрявый?"), sheep1.morning("А тебя подстрижем, Барашек?")
        print()

        # Кормим животных и перепроверяем их вес
        cow.feed()
        goose0.feed(), goose1.feed()
        duck.feed()
        chicken0.feed(), chicken1.feed()
        shegoat.feed()
        sheep0.feed(), sheep1.feed()
        print()

        pprint(Cattle.show_cattle(), indent=0, compact=True)
        print()

        # Собираем с животных дань :)
        cow.milk()
        goose0.collect_eggs(), goose1.collect_eggs()
        duck.collect_eggs()
        chicken0.collect_eggs(), chicken1.collect_eggs()
        shegoat.milk()
        sheep0.shear(), sheep1.shear()
        print()

        # Выгуливаем всех
        cow.pasture()
        goose0.pasture(), goose1.pasture()
        duck.pasture()
        chicken0.pasture(), chicken1.pasture()
        shegoat.pasture()
        sheep0.pasture(), sheep1.pasture()
        print()

        # Возвращаем домой. После прогулки hunger=True и животные опять хотят есть
        cow.come_back(choice(reasons))
        goose0.come_back(), goose1.come_back()
        duck.come_back()
        chicken0.come_back(), chicken1.come_back()
        shegoat.come_back()
        sheep0.come_back(), sheep1.come_back()
        print()

        # Кормим животных и перепроверяем их вес
        cow.feed()
        goose0.feed(), goose1.feed()
        duck.feed()
        chicken0.feed(), chicken1.feed()
        shegoat.feed()
        sheep0.feed(), sheep1.feed()
        print()

        pprint(Cattle.show_cattle(), indent=0, compact=True)
        print()

        # А если перед сном опять попробовать собрать ресурсы?
        cow.milk()
        goose0.collect_eggs(), goose1.collect_eggs()
        duck.collect_eggs()
        chicken0.collect_eggs(), chicken1.collect_eggs()
        shegoat.milk()
        sheep0.shear(), sheep1.shear()
        print()

        # Находим вес всех животных и самое тяжелое из них
        animals = Cattle.show_cattle()
        print("Общий вес всех животных на ферме:", Cattle.get_weight())
        print("Самое тяжелое из них:", max(animals, key=lambda animal: animals[animal]))
        print()

        # Укладываем всех спать. Сон генерирует яйца, молоко, и шерсть
        cow.sleep()
        goose0.sleep(), goose1.sleep()
        duck.sleep()
        chicken0.sleep(), chicken1.sleep()
        shegoat.sleep()
        sheep0.sleep(), sheep1.sleep()
        print()
        days -= 1


main()
