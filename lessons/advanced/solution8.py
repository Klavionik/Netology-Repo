import csv
import re
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from bson.regex import Regex

client = MongoClient('localhost', 27017)
db = client.netology


def read_data(filename):
    collection = db.events
    documents = []

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Цена'] = int(row['Цена'])
            row['Дата'] = datetime.strptime(row['Дата'] + '.20', '%d.%m.%y')
            documents.append(dict(row))

    collection.insert_many(documents)

    return documents


def find_cheapest(database):
    collection = database.events
    result = collection.find({}, {"_id": 0}).sort("Цена", ASCENDING)

    return result


def find_by_name(name, database):
    collection = database.events
    name = re.escape(name)
    pattern = re.compile('.*' + f'{name}' + '.*', re.IGNORECASE)
    regex = Regex.from_native(pattern)

    result = collection.find({"Исполнитель": regex}, {"_id": 0}).sort("Исполнитель", ASCENDING)

    return result


def find_by_date(database, start, end):
    collection = database.events
    start = datetime.strptime(start, '%d.%m.%Y')
    end = datetime.strptime(end, '%d.%m.%Y')

    if start == end:
        result = collection.find({"Дата": {"$eq": start}},
                                 {"_id": 0}).sort("Дата", ASCENDING)
    else:
        result = collection.find({"$and":
                                 [{"Дата": {"$lt": end}}, {"Дата": {"$gt": start}}]},
                                 {"_id": 0}).sort("Дата", ASCENDING)

    return result


if __name__ == '__main__':

    read_data('resources/artists.csv')
    print("Данные импортированы!\n")
    
    for event in find_cheapest(db):
        print(f'{event["Исполнитель"]}, '
              f'{event["Место"]}, '
              f'Цена {event["Цена"]}, '
              f'{datetime.strftime(event["Дата"], "%d %B %Y")}')
    
    artist = input("\nВведите название артиста для поиска\n")
    
    for event in find_by_name(artist, db):
        print(f'{event["Исполнитель"]}, '
              f'{event["Место"]}, '
              f'Цена {event["Цена"]}, '
              f'{datetime.strftime(event["Дата"], "%d %B %Y")}')

    date1 = input('\nВведите дату начала поиска в формате дд.мм.гггг\n')
    date2 = input('\nВведите дату окончания поиска в формате дд.мм.гггг\n')

    for event in find_by_date(db, date1, date2):
        print(f'{event["Исполнитель"]}, '
              f'{event["Место"]}, '
              f'Цена {event["Цена"]}, '
              f'{datetime.strftime(event["Дата"], "%d %B %Y")}')
