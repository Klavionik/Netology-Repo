"""
LESSON 2.1: EX. 2
"""

import unittest
import requests
from random import choice
from string import ascii_letters

API = "https://translate.yandex.net/api/v1.5/tr.json/translate"
API_KEY = "trnsl.1.1.20191127T183441Z.e41d27f588e08d59.579750edc0ce997528432fca22a5417f485ed432"


class TestYandexTranslateAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        text = ''.join([choice(ascii_letters) for _ in range(0, 1024 * 11)])

        cls.success = requests.get(API, params=dict(key=API_KEY, lang='en-ru', text='hello')).json()
        cls.incorrect_API = requests.get(API, params=dict(key='NO_KEY', lang='en-ru', text='hello')).json()
        cls.incorrect_lang = requests.get(API, params=dict(key=API_KEY, lang='xx-zz', text='hello')).json()
        cls.incorrect_size = requests.post(API, params=dict(key=API_KEY, lang='en-ru'), data={'text': text}).json()

    def test_status(self):
        self.assertEqual(self.success['code'], 200, msg='Unsuccessful response')
        self.assertEqual(self.incorrect_API['code'], 401, msg='Incorrect API key check failed')
        self.assertEqual(self.incorrect_lang['code'], 501, msg='Incorrect language pair check failed')
        self.assertEqual(self.incorrect_size['code'], 413, msg='Maximum text size check failed')

    def test_translation(self):
        self.assertEqual(self.success['text'][0], 'привет', msg="Incorrect translation")


if __name__ == '__main__':
    unittest.main(verbosity=2)
