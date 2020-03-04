import configparser
import os

root = os.path.dirname(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read_file(open(os.path.join(root, 'config.ini')))

# Console coloring
G = '\033[38;5;40m'  # green
Y = '\033[38;5;220m'  # yellow
R = '\033[38;5;196m'  # red
B = '\033[38;5;15m'  # bold
V = '\033[38;5;31m'  # violet
END = '\033[0m'  # end of coloring

# App
# client ID
CLIENT_ID = config.get('App Settings', 'ClientID',
                       fallback=os.environ.get('CLIENT_ID'))
# user-agent
USER_AGENT = config.get('App Settings', 'UserAgent')


# VK API general
API_URL = config.get('VK API', 'APIUrl')
AUTHORIZE_URL = config.get('VK API', 'AuthorizeUrl')
REDIRECT_URI = config.get('VK API', 'RedirectUrl')
VERSION = config.get('VK API', 'Version')

# Directories paths
data = os.path.join(root, 'data')
resources = os.path.join(root, 'resources')
# Serialized token path
tokenpath = os.path.join(data, 'token.dat')
# SQLite database path
dbpath = os.path.join(data, "vkinder.db")

# VK user object item fields -> :class:`User` attributes mapping
user_map = {'general': config['General User'],
            'interests': config['Interests'],
            'personal': config['Personal']}

# VK user object item fields -> :class:`Match` attributes mapping
match_map = {'general': config['General Match'],
             'interests': config['Interests'],
             'personal': config['Personal']}

# VK photo sizes map (from biggest to smallest)
photo_sizes = {k: int(v) for k, v in config['Photo Sizes'].items()}

# Match settings: score weight
PERSONAL_FACTOR = config.getint('Match Settings', 'PersonalFactor')
INTERESTS_FACTOR = config.getint('Match Settings', 'InterestsFactor')
FRIENDS_FACTOR = config.getint('Match Settings', 'FriendsFactor')
GROUPS_FACTOR = config.getint('Match Settings', 'GroupsFactor')
AGE_BOUND = config.getint('Match Settings', 'AgeBound')
