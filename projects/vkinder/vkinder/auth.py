import pickle
import re
from getpass import getpass

import mechanize
import requests
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session

from .api import vkrequest
from .globals import *
from .utils import clean_screen

br = mechanize.Browser()
br.set_handle_robots(False)
tokenpattern = re.compile(r'(https://login\.vk\.com/\?act=grant_access.*?html)')


def get_token(discard_token):
    """
    Establishes an OAuth2 session to retrieve a token for further API requests.
    Saves retrieved token to a file.

    :param discard_token:
    :return: VK API token
    """
    print(f'{Y}{USER_AGENT}\nWe need to authorize you with VK{END}\n')

    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID),
                       redirect_uri=REDIRECT_URI,
                       scope="friends, groups, offline, photos") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL)
        br.open(authorization_url)
        login_attempts = 3
        while login_attempts > 0:
            if AUTHORIZE_URL in br.geturl():
                br.select_form(nr=0)
                print(f'Login attempts left: {login_attempts}')
                br.form['email'] = input('Enter your VK email or phone number:\n')
                br.form['pass'] = getpass('Enter your VK password:\n')
                br.submit()
            else:
                break
            login_attempts -= 1
        else:
            print("Invalid login and/or password!")
            exit()
        if 'authcheck' in br.geturl():
            br.select_form(nr=0)
            br.form['code'] = input('Enter authentication code\n')
            br.submit()
        try:
            response = br.response()
            decoded = response.get_data().decode('cp1251')
            match = re.search(tokenpattern, decoded)
            link = match.group(0)
            br.open(link)
        except AttributeError:
            pass

        vk.token_from_fragment(br.geturl())
        token = vk.access_token

        if not discard_token:
            save_token(token)

    return token


def open_token():
    """
    Reads VK API token from a saved file.
    :return: VK API token
    """
    with open(tokenpath, "rb") as f:
        token = pickle.load(f)

    return token


@vkrequest
def test_request(token):
    """
    Sends a test request to ensure authorization went right.

    :param token: VK API token
    :return: App owner info
    """
    params = {'v': VERSION, 'access_token': token}
    test_response = requests.get(API_URL + '/users.get', params)

    return test_response


def save_token(token):
    """
    Saves VK API token to a file.
    :param token: VK API token
    """
    with open(tokenpath, "wb") as f:
        pickle.dump(token, f)


def authorize(discard_token=False):
    """
    Handles authorization process at the start of the application.
    Tries to read token from a file and if it fails, runs get_token()
    to obtain a new token from a user.

    :param discard_token: If True saves token to a file
    :return: Token, token owner id
    """

    try:
        token = open_token()
    except FileNotFoundError:
        token = get_token(discard_token)

    response = test_request(token)
    owner_name = response[0]['first_name']
    owner_surname = response[0]['last_name']
    clean_screen()

    print(f"{G}Authorized as: {owner_name} {owner_surname}{END}")

    return token
