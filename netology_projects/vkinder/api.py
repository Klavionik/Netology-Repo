import requests

from netology_projects.vkinder.exceptions import APIError
from netology_projects.vkinder.globals import *


def users_search(auth, criteria):
    params = {**auth, **criteria}

    response = requests.get(API_URL + users_api.search, params=params)

    if response.status_code == 200:
        json_response = response.json()
        if 'response' not in json_response:
            raise APIError(json_response)

        users = json_response['response']['items']
        count = json_response['response']['count']

        return users, count
    else:
        response.raise_for_status()


def execute(auth, code):
    params = {**auth, 'code': code}

    response = requests.post(API_URL + others_api.execute, data=params)

    if response.status_code == 200:
        json_response = response.json()
        if ('response' not in json_response) or ("execute_errors" in json_response):
            raise APIError(json_response)

        result = json_response['response']

        return result
    else:
        response.raise_for_status()


def groups_get(auth, user_id, count=1000):
    params = {**auth, 'user_id': user_id, 'count': count}

    response = requests.get(API_URL + groups_api.get, params=params)

    if response.status_code == 200:
        json_response = response.json()
        if 'response' not in json_response:
            raise APIError(json_response)

        groups = json_response['response']['items']

        return groups
    else:
        response.raise_for_status()


def users_get(auth, user_ids, fields):
    params = {**auth, 'user_ids': f'{user_ids}'.strip('[]'), 'fields': fields}

    response = requests.post(API_URL + users_api.get, data=params)

    if response.status_code == 200:
        json_response = response.json()
        if 'response' not in json_response:
            raise APIError(json_response)

        users = json_response['response']

        return users
    else:
        response.raise_for_status()


def get_cities(auth, city_name, count=1):
    params = {**auth, 'country_id': 1, 'q': city_name, 'count': count}

    response = requests.get(API_URL + others_api.getcities, params=params)

    if response.status_code == 200:
        json_response = response.json()
        if 'response' not in json_response:
            raise APIError(json_response)

        users = json_response['response']

        return users
    else:
        response.raise_for_status()
