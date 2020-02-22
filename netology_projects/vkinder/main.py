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

import sys
import os
from vkinder import app
from vkinder.globals import AMOUNT, R, G, Y, END, B


def main():
    """
    Options:

        -u (user) - set current app user
        -f (find) - find/refresh matches for the current user
        -n (next) - export next best matches for a user to a JSON file
        -l (list) - list saved users
        -q (quit) - quit app\n
    """

    if sys.platform == "win32":
        os.system("cls")
        os.system("color")
    elif sys.platform == "linux":
        os.system("clear")

    vkinder = app.startup()
    print(f'{B}{__doc__}{END}')

    while True:
        print(f'{B}{main.__doc__}{END}')
        option = input()
        if option == '-u':

            target = input(f"{Y}Let's find somebody's fortune! "
                           "But first, enter their ID or screenname below.\n"
                           "We'll need to acquire some information about the lucky guy "
                           f"or girl.{END}\n")
            new_user = vkinder.new_user(target)
            print(f'{G}{new_user} set as the current user.{END}')

        elif option == '-f':

            if vkinder.current_user:
                print(f"\n{G}Please, wait a minute while we're collecting data...{END}\n")
                found = vkinder.spawn_matches()
                print(f'\n{G}{found} matches found and saved.{END}')
            else:
                print(f'{R}No current user set.{END}')

        elif option == '-n':

            if not vkinder.current_user:
                target = input(f'{Y}No current user set.\n'
                               f'Enter user id to export next {AMOUNT} matches.{END}\n')
            else:
                target = vkinder.current_user.uid
            exported = vkinder.next_match(target)
            if exported is not False:
                print(f'{G}{exported} records exported to the data folder.{END}')
            else:
                print(f'{R}User not found.{END}')

        elif option == '-l':
            vkinder.list_users()
        elif option == '-q':
            quit()


if __name__ == '__main__':
    main()
