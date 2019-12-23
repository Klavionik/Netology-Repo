"""
LESSON 1.2, EX. 1, 2.
"""

import hashlib
import json
from time import sleep


# EX. 1
class JSONIterator:

    def __init__(self, file):
        with open(file) as f:
            self.file = json.load(f)
        self.item = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.item += 1
        try:
            country_name = self.file[self.item]['name']['common']
            link = f"https://en.wikipedia.org/wiki/{country_name.replace(' ', '_')}"
        except IndexError:
            raise StopIteration
        return country_name, link

    def process(self):
        with open("links.txt", 'w', encoding='utf-8') as f:
            for country in self:
                f.write(f'{country[0]} - {country[1]}\n')
        print("\nSaved to links.txt")


# EX. 2
def md5_hash_gen(filename):
    hash_point = hashlib.md5()
    with open(filename, 'rb') as fhandle:
        file = fhandle.read()
    for line in file:
        hash_point.update(bytes(line))
        yield hash_point.hexdigest()


if __name__ == '__main__':
    json_fname = input("Enter a JSON filename:\n")
    json_gen = JSONIterator(json_fname)
    json_gen.process()

    fname = input("Enter a filename:\n")
    hash_gen = md5_hash_gen(fname)
    for hashed_line in hash_gen:
        print(hashed_line)
        sleep(0.4)