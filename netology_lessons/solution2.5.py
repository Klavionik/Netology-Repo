""""
ЛЕКЦИЯ 2.5, ЗАДАЧА 1, 2
"""

from contextlib import contextmanager
from random import randint
from time import sleep
from datetime import datetime


@contextmanager
def uptime():
    start = datetime.now()
    try:
        yield
    finally:
        end = datetime.now()
        duration = end - start
        print(f"Сеанс связи начат {start}\n"
              f"Сеанс связи окончен {end}\n"
              f"Продолжительность сеанса {duration}")


# Программа эмулирует выход разведчика на связь с центром, получение
# неких инструкций в виде кодов и запись в блокнот разведчика (файл).
# Время выполнения составит 27 секунд (сумма всех sleep()).
def main():
    with uptime():
        print("ПОЛУЧЕНИЕ ШИФРОВКИ ИЗ ЦЕНТРА\n\nСоединение с центром...", end=" ")
        with open("message.txt", "w", encoding="utf-8") as notebook:
            sleep(5)
            print("УСПЕШНО")
            print("Прием сообщения...")
            for i in range(5):
                sleep(3)
                code = str(randint(1000, 9999))
                notebook.write(f"{code}\n")
                print(code)
            print("Закрытие сеанса связи...", end=" ", flush=True)
            sleep(5)
            print("УСПЕШНО")
        sleep(2)
        print("Сообщение принято и записано\n")


main()

