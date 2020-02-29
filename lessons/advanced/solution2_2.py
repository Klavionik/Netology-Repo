import re
import csv
from pprint import pprint


def prepare_data(path):
    with open(path, newline='', encoding='utf-8') as f:
        data = [row for row in csv.reader(f)]
    return data


def fix_names(data):
    for row in data[1:]:
        full_name = row[0:3]
        joined_fname = ''.join(full_name)
        found = re.findall(r'[А-Я][а-я]+', joined_fname)
        for i in range(0, len(found)):
            row[i] = found[i]
    return data


def remove_duplicates(data):
    last_names = []
    for contact in data[1:]:
        last_names.append(contact[0])

    duplicates = {}
    for index, name in enumerate(last_names):
        if last_names.count(name) > 1:
            if last_names.index(name) not in duplicates:
                duplicates[last_names.index(name)] = []
            duplicates[last_names.index(name)].append(data[index + 1])

    for name, duplicate in duplicates.items():
        index = 0
        for d1, d2 in zip(*duplicate):
            if not d1:
                duplicates[name][0][index] = d2
            index += 1
        data.remove(duplicates[name].pop(1))

    return data


def fix_phones(data, regexp):

    for row in data[1:]:
        phone = regexp.sub(r'+7(\2)\3-\4-\5 \6', row[5])
        row[5] = phone.rstrip()

    return data


def dump_data(data):

    with open("phonebook_processed.csv", "w", newline='', encoding='utf-8') as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(data)
    return


if __name__ == '__main__':
    path = 'resources/phonebook_raw.csv'

    # read data from csv source
    phonebook = prepare_data(path)

    # rearrange names, surnames, last names
    fixed_names = fix_names(phonebook)

    # merge duplicate entries
    fixed_duplicates = remove_duplicates(fixed_names)

    pattern = re.compile(r'^(\+7|8)+\s?\(?(\d{3})\)?-?\s?-?\s?(\d{3})-?(\d{2})-?(\d{2})\s?\(?(\w+\.\s\d+)?\)?')

    # format phone numbers
    fixed_phones = fix_phones(fixed_duplicates, pattern)

    # save processed data
    dump_data(fixed_phones)

    pprint(fixed_phones)







