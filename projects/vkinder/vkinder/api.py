from collections import namedtuple

import requests

from vkinder.exceptions import APIError
from vkinder.globals import API_URL

UsersMethods = namedtuple('Users', 'get search')
GroupsMethods = namedtuple('Groups', 'get')
OtherMethods = namedtuple('Others', 'getcities execute getshortlink')

users_api = UsersMethods(get='/users.get', search='/users.search')
groups_api = GroupsMethods(get='/groups.get')
others_api = OtherMethods(getcities='/database.getCities', execute='/execute',
                          getshortlink='/utils.getShortLink')


def vkrequest(methodfunc):
    """
    Wraps a function that returns a response from the VK API,
    checks if received response is correct and unpacks it.
    Raises `requests` lib `HTTPError` exception if response status
    if not 200 `OK`.

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


class VKApi:

    def __init__(self, api_url, api_version, token):
        self.url = api_url
        self.v = api_version
        self.token = token
        self.auth = {'v': self.v, 'access_token': self.token}

    @vkrequest
    def users_search(self, criteria):
        """
        Makes a request to the VK API `users.search` method and
        returns the contents of the response.

        :param criteria: Search criteria
        :return: Matching users
        """
        params = {**self.auth, **criteria}

        response = requests.get(API_URL + users_api.search, params=params)

        return response

    @vkrequest
    def execute(self, code):
        """
        Makes a request to the VK API `execute` method and
        returns results of the request.

        :param code: VKScript code
        :return: Results of the execution
        """
        params = {**self.auth, 'code': code}

        response = requests.post(API_URL + others_api.execute, data=params)

        return response

    @vkrequest
    def groups_get(self, user_id, count=1000):
        """
        Makes a request to the VK API `groups.get` method and
        returns a list of user's groups.

        :param user_id: VK user id
        :param count: Amount of groups to return
        :return: List of group ids
        """
        params = {**self.auth, 'user_id': user_id, 'count': count}

        response = requests.get(API_URL + groups_api.get, params=params)

        return response

    @vkrequest
    def users_get(self, user_ids, fields):
        """
        Makes a request to the VK API `users.get` method and
        returns detailed profile info of the given user ids.

        :param user_ids: VK user ids (up to 1000 per request)
        :param fields: Additional profile fields to return
        :return: List of VK `User` objects
        """
        params = {**self.auth, 'user_ids': f'{user_ids}'.strip('[]'), 'fields': fields}

        response = requests.post(API_URL + users_api.get, data=params)

        return response

    @vkrequest
    def get_cities(self, city_name, count=1):
        """
        Makes a request to the VK API `database.getCities` method and
        returns the contents of the response.

        :param city_name: Search query for the method
        :param count: Number of cities to return
        :return: List of cities
        """
        params = {**self.auth, 'country_id': 1, 'q': city_name, 'count': count}

        response = requests.get(API_URL + others_api.getcities, params=params)

        return response
