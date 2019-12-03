
"""
ЛЕКЦИЯ 3.2, ЗАДАЧА 1, 2
"""

import webbrowser
import requests
from requests_oauthlib import OAuth2Session
from time import sleep


TRANSLATE_API = 'trnsl.1.1.20191127T183441Z.e41d27f588e08d59.579750edc0ce997528432fca22a5417f485ed432'
TRANSLATE_URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

# TODO 1: Заменить CLIENT_ID и CLIENT_SECRET на id и пароль приложения
CLIENT_ID = "INSERT_CLIENT_ID"
CLIENT_SECRET = "INSERT_CLIENT_SECRET"

CLOUD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
REDIRECT_URI = "https://oauth.yandex.ru/verification_code"
AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
TOKEN_URL = "https://oauth.yandex.ru/token"


def main():
    print("\nДобро пожаловать!\n")  # Быть вежливым - это важно
    while True:
        print('Укажите направление перевода (например, de-ru для перевода с немецкого '
              'языка на русский).\nНажмите Enter чтобы выполнить перевод по умолчанию (на русский с '
              'автоматическим определением языка источника).\nВведите quit для выхода.\n')
        try:
            lang_pair = input()
            if lang_pair == "quit":
                break
            from_lang, to_lang = lang_pair.lower().strip().split('-')
        # Если языковая пара не указана, или указана в некорректном формате,
        # язык текста: автоматически, язык перевода: русский
        except ValueError:
            from_lang, to_lang = 1, "ru"

        source = input("\nУкажите путь к файлу или введите текст для перевода\n\n").strip()

        # В этой ветке работа с файлом
        if source.endswith(".txt"):
            target_file = input("\nУкажите путь к файлу, в который будет сохранен результат перевода\n\n").strip()

            # Открытие файла, перевод содержимого, запись перевода в новый файл
            try:
                with open(source, encoding="utf-8") as source_file:
                    source_text = source_file.read()

                text_translated = translate(source_text, from_lang, to_lang)

                with open(target_file, "w", encoding="utf-8") as result:
                    result.write(text_translated)
                print(f"\nРезультат перевода сохранен в файл {target_file}")
            except FileNotFoundError:
                print("Указанный файл не найден")
                continue

            # Опция выгрузки файла на Яндекс.Диск
            upload_choice = input("Загрузить файл на Яндекс.Диск? (да|нет)\n\n").lower().strip()
            if upload_choice == "да":
                upload_yadisk(target_file)
            else:
                continue

        # В этой ветке работа со строкой: перевод и вывод перевода
        else:
            string_translated = translate(source, from_lang, to_lang)
            print(f'Результат: {string_translated}\n')


def translate(text, from_lang, to_lang):
    # Параметры для перевода по умолчанию
    if from_lang == 1:
        params = {
            'key': TRANSLATE_API,
            'text': text,
            'lang': to_lang,
            "options": 1,
        }
    # Параметры для перевода в указанной пользователем языковой паре
    else:
        params = {
            'key': TRANSLATE_API,
            'text': text,
            'lang': f'{from_lang}-{to_lang}',
        }
    # Получение ответа от API Яндекс.Переводчика
    translate_response = requests.post(TRANSLATE_URL, params=params)
    translate_response_json = translate_response.json()

    # Проверка кода ответа, возврат перевода или ошибки
    try:
        assert translate_response.status_code == 200
        translation = translate_response_json["text"]
        return ''.join(translation)
    except AssertionError:
        error = translate_response_json["message"]
        print(f"Ошибка при работе с API:\n{error}")
        return "Отсутствует"


def upload_yadisk(filename):
    # Параметры получения ссылки для загрузки.
    # Имя файла будет таким же, как и на локальном диске,
    # файл появится в корневом каталоге Яндекс.Диска,
    # если файл c таким именем уже есть, он будет перезаписан.
    params = {
        'path': filename,
        'overwrite': 'true',
        'fields': 'href'
    }

    # Авторизация через Яндекс.OAuth, получение токена для доступа к аккаунту
    with OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI) as oauth:
        print("\nДля загрузки файла необходимо авторизоваться.\nВ открывшейся вкладке браузера "
              "разрешите приложению Netology Lesson 3.2 by Roman Vlasenko\n"
              "доступ к вашему аккаунту Яндекс.Диск и скопируйте код подтверждения\n")
        sleep(8)  # Чтобы было время прочитать текст выше :)

        # Авторизация через код подтверждения
        authorization_url, state = oauth.authorization_url(AUTHORIZE_URL)
        webbrowser.open_new_tab(authorization_url)
        authorization_code = input("Введите код подтверждения:\n\n")

        # Получение токена из ответа
        try:
            receive_token = oauth.fetch_token(TOKEN_URL, code=authorization_code,
                                              include_client_id=True, client_secret=CLIENT_SECRET)
            token = receive_token["access_token"]
        except Exception as error:
            print(f"Не удалось закончить авторизацию:\n{error}\n")
            return

    # Получение ссылки для загрузки файла, используя токен
    headers = {"Authorization": f"{token}"}
    response_link = requests.get(CLOUD_URL, params=params, headers=headers)
    response_link_json = response_link.json()

    try:
        assert response_link.status_code == 200
        upload_target = response_link_json["href"]
    except AssertionError:
        error = response_link.json()["message"]
        print(f"Не удалось получить ссылку для загрузки:\n{error}")

    # Загрузка файла на Яндекс.Диск, токен уже не нужен
    else:
        try:
            with open(filename, "rb") as file:
                response_upload = requests.put(upload_target, data=file)
                assert response_upload.status_code == 201
                print("Загрузка завершена успешно!\n\n")
        except AssertionError:
            error = response_upload.json()["message"]
            print(f"Не удалось завершить загрузку:\n{error}")


if __name__ == '__main__':
    main()
