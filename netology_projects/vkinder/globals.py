import os
from collections import namedtuple

# namedtuples to store VK API methods
UsersMethods = namedtuple('Users', 'get search')
GroupsMethods = namedtuple('Groups', 'get')
OtherMethods = namedtuple('Others', 'getcities execute')

# App client ID
CLIENT_ID = os.environ['CLIENT_ID']

# Chrome driver path for Selenium
CHROMEDRIVER = os.environ['CHROMEDRIVER']

# General VK API constants
API_URL = "https://api.vk.com/method"
AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
REDIRECT_URI = 'https://oauth.vk.com/blank.html'
VERSION = 5.103

# VK API methods
users_api = UsersMethods(get='/users.get', search='/users.search')
groups_api = GroupsMethods(get='/groups.get')
others_api = OtherMethods(getcities='/database.getCities', execute='/execute')

# Root and data directories
root = os.path.dirname(os.path.abspath(__file__))
data = os.path.join(root, 'data')
resources = os.path.join(root, 'resources')

# required fields for users.get method
req_fields = 'bdate,city,sex,common_count,games,music,movies,interests,tv,books,personal'

# VK user object item fields -> :class: User attributes mapping
user_attr_map = {'id': 'uid',
                 'first_name': 'name',
                 'last_name': 'surname',
                 'bdate': 'age',
                 'sex': 'sex',
                 'city.id': 'city',
                 'interests': 'interests.interests',
                 'music': 'interests.music',
                 'movies': 'interests.movies',
                 'tv': 'interests.tv',
                 'books': 'interests.books',
                 'games': 'interests.games',
                 'personal.political': 'personal.political',
                 'personal.religion': 'personal.religion',
                 'personal.people_main': 'personal.people_main',
                 'personal.life_main': 'personal.life_main',
                 'personal.smoking': 'personal.smoking',
                 'personal.alcohol': 'personal.alcohol'
                 }

# VK user object item attributes -> :class: Match attributes mapping
match_attr_map = {**user_attr_map, 'common_friends': 'common_friends'}

# Measures schema:
# mandatory: sex > age > city
# optional: common interests > personal > common friends > common groups

# Age bound
age_bound = 3
