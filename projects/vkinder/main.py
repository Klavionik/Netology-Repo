"""
VKInder: a coursework for Netology Python course by Roman Vlasenko

GOAL: implement a Tinder-like app which, given a VK user id
or a screenname, finds the most compatible pairs for the user
amongst the other VK users.

The application collects all the information it needs
through the VK API and user input, finds the matches,
assigns each match a score based on the likeness of
user's and match's profile, saves matches to the database
and exports matches from the database in JSON format files
in descending score order.
"""
import os
from vkinder import app as vkinder
from vkinder.globals import AMOUNT, R, G, Y, END, B


def main():
    """
    Options:

        u (user) - set current app user
        f (find) - find/refresh matches for the current user
        n (next) - export next best matches for a user to a JSON file
        l (list) - list saved users
        q (quit) - quit app\n
    """

    os.system("color")
    app = vkinder.startup()
    print(f'{B}{__doc__}{END}')

    while True:
        print(f'{B}{main.__doc__}{END}')
        option = input()

        if option == 'u':
            set_user(app)
        elif option == 'f':
            find_matches(app)
        elif option == 'n':
            next_matches(app)
        elif option == 'l':
            list_users(app)
        elif option == 'q':
            quit()


def set_user(app):
    target = input(f"{Y}Let's find somebody's fortune! "
                   "But first, enter their ID or screenname below.\n"
                   "We'll need to acquire some information about the lucky guy "
                   f"or girl.{END}\n")
    new_user = app.new_user(target)
    print(f'{G}{new_user} set as the current user.{END}')


def find_matches(app):
    if app.current_user:
        print(f"\n{G}Please, wait a minute while we're collecting data...{END}\n")
        found = app.spawn_matches()
        print(f'\n{G}{found} matches found and saved.{END}')
    else:
        print(f'{R}No current user set.{END}')


def next_matches(app):
    if not app.current_user:
        target = input(f'{Y}No current user set.\n'
                       f'Enter user id to export next {AMOUNT} matches.{END}\n')
    else:
        target = app.current_user.uid

    exported = app.next_matches(target)
    if exported is not False:
        print(f'{G}{exported} records exported to the data folder.{END}')
    else:
        print(f'{R}User not found.{END}')


def list_users(app):
    users_list = app.list_users()
    if users_list is not False:
        for user in users_list:
            print(f'{G}{user["name"]} {user["surname"]} '
                  f'Age {user["age"]} ID {user["uid"]}{END}')
    else:
        print(f'{R}No saved users.{END}')


if __name__ == '__main__':
    main()
