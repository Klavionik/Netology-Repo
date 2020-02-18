import os

# App
# client ID
CLIENT_ID = os.environ['CLIENT_ID']
# user-agent
USER_AGENT = 'VKInder/0.1 (Windows NT 10.0; Win64; x64)'
# chrome driver path for Selenium
CHROMEDRIVER = os.environ['CHROMEDRIVER']

# VK API general
API_URL = "https://api.vk.com/method"
AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
REDIRECT_URI = 'https://oauth.vk.com/blank.html'
VERSION = 5.103

# Directories paths
root = os.path.dirname(os.pardir)
data = os.path.join(root, 'data')
resources = os.path.join(root, 'resources')
# Serialized token path
tokenpath = os.path.join(data, 'token.dat')
# SQLite database path
dbpath = f'sqlite:///{os.path.join(data, "vkinder.db")}'

# required fields for main.App._set_user method
req_fields = 'bdate,city,sex,common_count,games,music,movies,interests,tv,books,personal'

# VK user object item fields -> :class:`User` attributes mapping
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

# VK user object item attributes -> :class:`Match` attributes mapping
match_attr_map = {**user_attr_map, 'common_friends': 'common_friends'}

# VK photo sizes map (from biggest to smallest)
photo_sizes = {'w': 9, 'z': 8, 'y': 7, 'r': 6, 'q': 5, 'p': 4, 'o': 3, 'x': 2, 'm': 1, 's': 0}

# Optional measures:
# personal > common interests > common friends > common groups
PERSONAL_FACTOR = 50
INTERESTS_FACTOR = 30
FRIENDS_FACTOR = 15
GROUPS_FACTOR = 5

# Age bound
AGE_BOUND = 3
