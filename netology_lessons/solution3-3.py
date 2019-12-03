"""
ЛЕКЦИЯ 3.3, ЗАДАЧА 1, 2, 3
"""

import webbrowser
import requests
from copy import deepcopy
from time import sleep
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session

API_URL = "https://api.vk.com/method"
AUTHORIZE_URL = "https://oauth.vk.com/authorize"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
# TODO 1: Заменить CLIENT_ID на id приложения
CLIENT_ID = "INSERT_CLIENT_ID"

users = {}


class VKPerson:

    def __init__(self, user_id, name, lastname):
        self.user_id = user_id
        self.name = name
        self.lastname = lastname
        self.link = f"https://vk.com/id{user_id}"
        self.friends = {}

    def __repr__(self):
        return f"{self.name} {self.lastname}"

    def __str__(self):
        return f"ID: {self.user_id} {self.name} {self.lastname} {self.link}"

    def __and__(self, other):
        return set(self.friends.keys()) & set(other.friends.keys())


def main():
    # Авторизация при запуске скрипта
    auth_params = {}
    authorized = False
    if not authorized:
        auth_params, authorized = authorize()

    print("\nПоиск общих друзей у пользователей ВКонтакте".center(30, "*"))
    while True:
        print("\nВведите add, чтобы добавить информацию о пользователе ВКонтакте\n"
              "Введите show, чтобы вывести список всех добавленных пользователей\n"
              "Введите quit, чтобы выйти\n"
              "Для поиска общих друзей используйте синтаксис <ID1> & <ID2>\n")

        key = input().strip().lower()
        try:
            if key == "quit":
                return
            elif key == "add":
                ids = input("Введите ID или псевдоним пользователя (screen name)\n"
                            "Вводя несколько ID, разделяйте их пробелом\n")
                # если не использовать deepcopy, после работы функций fetch_friends()
                # и fetch_user() у auth_params остаются лишние ключи
                fetch_user(ids, deepcopy(auth_params))
                fetch_friends(deepcopy(auth_params))
            elif key == "show":
                show_all()
            elif "&" in key:
                common(key)
            else:
                raise ValueError
        except ValueError:
            print("Неизвестная команда")
        except KeyError:
            print("Указанного ID нет в списке. Возможно, вы забыли добавить его?")
        except AssertionError as error:
            print("API вернул ошибку:", error)


def authorize():
    """
    Establishes an OAuth2 session to get a token for further API requests

    :return: Dictionary of authorization parameters (token and version)
    """
    print("Для работы программы необходимо авторизоваться!\nВ открывшейся вкладке браузера "
          "разрешите приложению Netology Lesson 3.3 by Roman Vlasenko доступ к вашему\n"
          "аккаунту ВКонтакте и скопируйте содержимое адресной строки\n")
    sleep(8)

    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID), redirect_uri=REDIRECT_URI,
                       scope="friends") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL, display="page")
        webbrowser.open_new_tab(authorization_url)
        vk_response = input("Вставьте сюда содержимое адресной строки браузера:\n").rstrip()
        vk.token_from_fragment(vk_response)

    params = {"v": 5.103,
              "access_token": vk.access_token
              }
    # блок ниже делает тестовый запрос и проверяет,
    # чтобы API возвращал валидные данные, иначе
    # вероятнее всего, авторизация не удалась
    authtest = requests.get(API_URL + "/users.get", params).json()
    try:
        assert "response" in authtest
        print(f"\nДобро пожаловать, {authtest['response'][0]['first_name']}")
        return params, True
    except AssertionError:
        print(f"Тестовый запрос вернул ошибку: {authtest['error']['error_msg']}\n"
              "Повторная попытка авторизации через 5 с")
        sleep(5)
        return main()


def add_friends(friend, user):
    """
    Creates a new VKPerson object and adds it to the user's instance "friends" attribute

    :param friend: Friend object returned from fetch_friends() via VK API
    :param user: Instance of VKPerson, which will acquire given friend
    """
    friend_id = str(friend["id"])
    friend_name, friend_lastname = friend["first_name"], friend["last_name"]
    user.friends[friend_id] = VKPerson(friend_id, friend_name, friend_lastname)


def add_user(user):
    """
    Creates a new VKPerson object and adds it to the users dictionary

    :param user: User object returned from fetch_user() via VK API
    """
    user_id = str(user["id"])
    user_name, user_lastname = user["first_name"], user["last_name"]
    users[user_id] = VKPerson(user_id, user_name, user_lastname)


def fetch_friends(params):
    """
    Fetches friends data from VK API and adds friends to VKPerson objects

    :param params: Dictionary of authorization parameters
    """
    # дата рождения дальше не используется, но без поля fields в
    # запросе метод API возвращает только ID друзей,
    # а не полноценные объекты пользователей с именем и фамилией
    params["fields"] = "bdate"

    for user_id, user_instance in users.items():
        params["user_id"] = user_id
        response = requests.get(API_URL + "/friends.get", params)
        friends_json = response.json()

        assert "response" in friends_json, f"{friends_json['error']['error_msg']}"

        for friend in friends_json["response"]["items"]:
            add_friends(friend, user_instance)


def fetch_user(user_ids, params):
    """
    Fetches user data from VK API

    :param user_ids: String containing VK user IDs to add
    :param params: Dictionary of request parameters
    """
    # ключи в поле user_ids должны быть разделены запятой
    params["user_ids"] = ",".join(user_ids.split())

    response = requests.get(API_URL + "/users.get", params)
    users_json = response.json()

    assert "response" in users_json, f"{users_json['error']['error_msg']}"

    for user in users_json["response"]:
        add_user(user)


def common(query):
    user1, user2 = [users[user.strip()] for user in query.split("&")]
    print(f"Общие друзья пользователей {user1!r} и {user2!r}:\n")
    common_friends = user1 & user2
    for friend in common_friends:
        print(user1.friends[friend])


def show_all():
    """
    Prints out all VKPerson objects
    """
    for user in users.values():
        print(f"{user}")


if __name__ == '__main__':
    main()
