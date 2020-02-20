from collections import namedtuple

import requests

from vkinder.exceptions import APIError
from vkinder.globals import API_URL

UsersMethods = namedtuple('Users', 'get search')
GroupsMethods = namedtuple('Groups', 'get')
OtherMethods = namedtuple('Others', 'getcities execute')

# VK API methods
users_api = UsersMethods(get='/users.get', search='/users.search')
groups_api = GroupsMethods(get='/groups.get')
others_api = OtherMethods(getcities='/database.getCities', execute='/execute')


def vkrequest(methodfunc):
    """
    Wraps a function that returns a response from the VK API,
    checls if received response is correct and unpacks it.
    Raises `requests` lib `HTTPError` if response status
    if not `OK`.

    :param methodfunc: Function that returns a response object
    :return: Unpacked response
    """
    def wrapper(*args, **kwargs):
        response = methodfunc(*args, **kwargs)

        if response.status_code == 200:
            json_response = response.json()
            if ('response' not in json_response) or ("execute_errors" in json_response):
                raise APIError(json_response)

            return json_response['response']
        else:
            response.raise_for_status()
    return wrapper


@vkrequest
def users_search(auth, criteria):
    """
    Makes a request to the VK API `users.search` method and
    returns the contents of the response.

    :param auth: Auth parameters
    :param criteria: Search criteria
    :return: Response dict
    """
    params = {**auth, **criteria}

    response = requests.get(API_URL + users_api.search, params=params)

    return response


@vkrequest
def execute(auth, code):
    """
    Makes a request to the VK API `execute` method and
    returns results of the request.

    :param auth: Auth parameters
    :param code: VKScript code
    :return: Results of the execution
    """
    params = {**auth, 'code': code}

    response = requests.post(API_URL + others_api.execute, data=params)

    return response


@vkrequest
def groups_get(auth, user_id, count=1000):
    """
    Makes a request to the VK API `groups.get` method and
    returns a list of user's groups.

    :param auth: Auth parameters
    :param user_id: VK user id
    :param count: Amount of groups to return
    :return: List of group ids
    """
    params = {**auth, 'user_id': user_id, 'count': count}

    response = requests.get(API_URL + groups_api.get, params=params)

    return response


@vkrequest
def users_get(auth, user_ids, fields):
    """
    Makes a request to the VK API `users.get` method and
    returns detailed profile info of the given user ids.

    :param auth: Auth parameters
    :param user_ids: VK user ids (up to 1000 per request)
    :param fields: Additional profile fields to return
    :return: List of VK `User` objects
    """
    params = {**auth, 'user_ids': f'{user_ids}'.strip('[]'), 'fields': fields}

    response = requests.post(API_URL + users_api.get, data=params)

    return response


@vkrequest
def get_cities(auth, city_name, count=1):
    """
    Makes a request to the VK API `database.getCities` method and
    returns the contents of the response.

    :param auth: Auth parameters
    :param city_name: Search query for the method
    :param count: Number of cities to return
    :return: Response dict
    """
    params = {**auth, 'country_id': 1, 'q': city_name, 'count': count}

    response = requests.get(API_URL + others_api.getcities, params=params)

    return response
