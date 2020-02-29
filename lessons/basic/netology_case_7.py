import csv

flats_list = list()

with open('output.csv', newline='', encoding='utf-8') as csvfile:
    flats_csv = csv.reader(csvfile, delimiter=';')
    flats_list = list(flats_csv)

# можете посмотреть содержимое файла с квартирами через print, можете - на вкладке output.csv
# print (flats_list)


# TODO 1:
# 1) Напишите цикл, который проходит по всем квартирам, и показывает только новостройки
# и их порядковые номера в файле
# 2) добавьте в код подсчет количества новостроек
quantity_newflats = 0
print("Порядковые номера (ID) новостроек:\n")
for flat in flats_list:
    if "новостройка" in flat:
        print("{}".format(flat[0]))
        quantity_newflats += 1
print("Всего новостроек: {}\n".format(quantity_newflats))

# TODO 2:
# 1) Сделайте описание квартиры в виде словаря, а не списка.
# Используйте следующие поля из файла output.csv: ID, Количество комнат;Новостройка/вторичка, Цена (руб).
flats_dict = []
for flat in flats_list[1:]:
    flat_info = {"ID": flat[0], "rooms": flat[1], "type": flat[2],
                 "price": flat[11]}
    flats_dict.append(flat_info)

# 2) Измените код, который создавал словарь для поиска квартир по метро так,
# чтобы значением словаря был не список ID квартир, а список описаний квартир
# в виде словаря, который вы сделали в п.1
subway_dict = {}
for flat in flats_list[1:]:
    subway = flat[3].replace("м.", "")
    for flat in flats_dict:
        if subway not in subway_dict.keys():
            subway_dict[subway] = list()
        subway_dict[subway].append(flat)

# 3) Самостоятельно напишите код, который подсчитывает и выводит, сколько квартир нашлось у каждого метро.
for subway in subway_dict.keys():
    if subway:
        print("У м. {} нашлось {} квартир".format(subway, len(subway_dict[subway])))
