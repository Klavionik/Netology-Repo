import configparser
import os

root = os.path.dirname(os.path.dirname(__file__))
data = os.path.join(root, 'data')
resources = os.path.join(root, 'resources')
tokenpath = os.path.join(data, 'token.dat')
dbpath = os.path.join(data, "vkinder.db")

config = configparser.ConfigParser()
config.read_file(open(os.path.join(root, 'config.ini')))

# Console coloring
G = '\033[38;5;40m'  # green
Y = '\033[38;5;220m'  # yellow
R = '\033[38;5;196m'  # red
B = '\033[38;5;15m'  # bold
V = '\033[38;5;31m'  # violet
END = '\033[0m'  # end of coloring
