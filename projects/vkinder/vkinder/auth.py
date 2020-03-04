import pickle
import re
from getpass import getpass

import mechanize
import requests
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session

import vkinder.globals as g
from .api import vkrequest
from .utils import clean_screen

browser = mechanize.Browser()
browser.set_handle_robots(False)
allowlink = re.compile(r'(https://login\.vk\.com/\?act=grant_access.*?html)')


def get_token(discard_token):
    """
    Establishes an OAuth2 session to retrieve a token for further API requests.
    Saves retrieved token to a file.

    :param discard_token: If True save token to a file
    :return: VK API token
    """
    print(f'{g.Y}{g.USER_AGENT}\nWe need to authorize you with VK{g.END}\n')

    with OAuth2Session(client=MobileApplicationClient(client_id=g.CLIENT_ID),
                       redirect_uri=g.REDIRECT_URI,
                       scope="friends, groups, offline, photos") as vk:
        authorization_url, state = vk.authorization_url(g.AUTHORIZE_URL)
        tokenurl = login(authorization_url)
        vk.token_from_fragment(tokenurl)
        token = vk.access_token

        if not discard_token:
            save_token(token)

    return token


def login(authorization_url, login_attempts=3):
    browser.open(authorization_url)
    while login_attempts:
        if g.AUTHORIZE_URL in browser.geturl():
            browser.select_form(nr=0)
            print(f'Login attempts left: {login_attempts}')
            browser.form['email'] = input('Enter your VK email or phone number:\n')
            browser.form['pass'] = getpass('Enter your VK password:\n')
            browser.submit()
        else:
            break
        login_attempts -= 1
    else:
        print("Invalid login and/or password!")
        exit()
    if 'authcheck' in browser.geturl():
        browser.select_form(nr=0)
        browser.form['code'] = input('Enter authentication code\n')
        browser.submit()
    try:
        raw_response = browser.response()
        decoded_response = raw_response.get_data().decode('cp1251')
        match = re.search(allowlink, decoded_response)
        link = match.group(0)
        permission = input("You are about to grant next permissions to this app:\n"
                           "Access to friends\n"
                           "Access to photos\n"
                           "Access to API at any time\n\n"
                           "Proceed? y/n").lower().rstrip()
        if permission != 'y':
            print('Aborted')
            exit()
        browser.open(link)
    except AttributeError:
        pass

    tokenurl = browser.geturl()
    return tokenurl


def open_token():
    """
    Reads VK API token from a saved file.
    :return: VK API token
    """
    with open(g.tokenpath, "rb") as f:
        token = pickle.load(f)

    return token


@vkrequest
def test_request(token):
    """
    Sends a test request to ensure authorization went right.

    :param token: VK API token
    :return: App owner info
    """
    params = {'v': 5.103, 'access_token': token}
    test_response = requests.get(g.API_URL + '/users.get', params)

    return test_response


def save_token(token):
    """
    Saves VK API token to a file.
    :param token: VK API token
    """
    with open(g.tokenpath, "wb") as f:
        pickle.dump(token, f)


def authorize(discard_token=False):
    """
    Handles authorization process at the start of the application.
    Tries to read token from a file and if it fails, runs get_token()
    to obtain a new token from a user.

    :param discard_token: If True save token to a file
    :return: VK API token
    """

    try:
        token = open_token()
    except FileNotFoundError:
        token = get_token(discard_token)

    response = test_request(token)
    owner_name = response[0]['first_name']
    owner_surname = response[0]['last_name']
    clean_screen()

    print(f"{g.G}Authorized as: {owner_name} {owner_surname}{g.END}")

    return token
