import pickle

import requests
from oauthlib.oauth2 import MobileApplicationClient
from requests_oauthlib import OAuth2Session
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

from netology_projects.vkinder.exceptions import APIError
from netology_projects.vkinder.globals import *

TOKEN_FILE = os.path.join(data, 'token.dat')
USER_AGENT = 'VKInder/0.1 (Windows NT 10.0; Win64; x64)'

# keeps Selenium from opening up a browser window and adds custom user-agent
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f'--user-agent={USER_AGENT}')
driver = webdriver.Chrome(CHROMEDRIVER, chrome_options=chrome_options)


def get_token(save):
    """
    Establishes an OAuth2 session to retrieve a token for further API requests.
    Saves retrieved token to a file.

    :return: Dictionary of authorization parameters
    """
    print('We need to authorize you with VK\n')

    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID), redirect_uri=REDIRECT_URI,
                       scope="friends, groups, offline, photos") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL)

        driver.get(authorization_url)
        form_email = driver.find_element_by_name("email")
        form_pass = driver.find_element_by_name("pass")
        form_email.send_keys(input('Enter your VK email or phone number\n'))
        form_pass.send_keys(input('Enter your VK password\n'))
        form_email.submit()
        try:
            security_check = driver.find_element_by_name('code')
            security_check.send_keys(input('Enter authentication code\n'))
            security_check.submit()
        except NoSuchElementException:
            pass
        try:
            allow = driver.find_element_by_xpath('//*[@id="oauth_wrap_content"]/div[3]/div/div[1]/button[1]')
            allow.click()
        except NoSuchElementException:
            pass

        vk.token_from_fragment(driver.current_url)
        token = vk.access_token

        if save:
            save_token(token)

    return token


def open_token():
    with open(TOKEN_FILE, "rb") as f:
        token = pickle.load(f)

    return token


def save_token(token):
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(token, f)


def authorize(save=True):
    user_id = None

    try:
        token = open_token()
    except FileNotFoundError:
        token = get_token(save)

    try:
        test_response = requests.get(API_URL + users_api.get, params={'v': VERSION, 'access_token': token}).json()
        if 'response' not in test_response:
            raise APIError(test_response)
        first_name, last_name = test_response['response'][0]['first_name'], test_response['response'][0]['last_name']
        user_id = test_response['response'][0]['id']
        print(f"User: {first_name} {last_name}")
    except APIError as error:
        print('API Error:', error.message, error.body)
        quit()

    return token, user_id
