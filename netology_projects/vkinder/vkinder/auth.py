import pickle

import os
import requests
from getpass import getpass
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from vkinder.exceptions import APIError
from vkinder.globals import *

# keeps Selenium from opening up a browser window and adds custom user-agent
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f'--user-agent={USER_AGENT}')
chrome_options.add_argument('log-level=2')
driver = webdriver.Chrome(DRIVER, chrome_options=chrome_options)

allow_button = r'//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]'


def get_token(save):
    """
    Establishes an OAuth2 session to retrieve a token for further API requests.
    Saves retrieved token to a file.

    :return: VK API token as a string
    """
    print(f'{Y}VKInder v0.4\nWe need to authorize you with VK{END}\n')

    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID),
                       redirect_uri=REDIRECT_URI,
                       scope="friends, groups, offline, photos") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL)

        driver.get(authorization_url)
        form_email = driver.find_element_by_name("email")
        form_pass = driver.find_element_by_name("pass")
        form_email.send_keys(input('Enter your VK email or phone number:\n'))
        form_pass.send_keys(getpass('Enter your VK password:\n'))
        form_email.submit()
        try:
            security_check = driver.find_element_by_name('code')
            security_check.send_keys(input('Enter authentication code:\n'))
            security_check.submit()
        except NoSuchElementException:
            pass
        try:
            allow = driver.find_element_by_xpath(allow_button)
            allow.click()
        except NoSuchElementException:
            pass

        vk.token_from_fragment(driver.current_url)
        token = vk.access_token

        if save:
            save_token(token)

    return token


def open_token():
    """
    Reads VK API token from a saved file.
    :return: VK API token as a string
    """
    with open(tokenpath, "rb") as f:
        token = pickle.load(f)

    return token


def save_token(token):
    """
    Saves VK API token to a file.
    :param token: VK API token as a string
    """
    with open(tokenpath, "wb") as f:
        pickle.dump(token, f)


def authorize(save=True):
    """
    Handles authorization process at the start of the application.
    Tries to read token from a file and if it fails, runs get_token()
    to obtain a new token from a user.

    :param save: Boolean value, False if you don't want the app
    to save the token to a file.
    :return: Tuple (token string, token owner id int)
    """
    user_id = None

    try:
        token = open_token()
    except FileNotFoundError:
        token = get_token(save)

    # make a test request to the API, quit if error occured
    try:
        params = {'v': VERSION, 'access_token': token}
        test_response = requests.get(API_URL + '/users.get', params).json()
        if 'response' not in test_response:
            raise APIError(test_response)
        first_name = test_response['response'][0]['first_name']
        last_name = test_response['response'][0]['last_name']
        user_id = test_response['response'][0]['id']
        os.system('cls')
        print(f"{G}Authorized as: {first_name} {last_name}{END}")
    except APIError as error:
        print(f'{R}API Error:{END}', error.message, error.body)
        quit()

    return token, user_id
