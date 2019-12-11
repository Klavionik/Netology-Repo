import requests
import json
import os
import sys
import webbrowser
import pickle
import argparse
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient
from time import sleep, time

# API constants
API_URL = "https://api.vk.com/method"
AUTHORIZE_URL = "https://oauth.vk.com/authorize"
REDIRECT_URI = "https://oauth.vk.com/blank.html"
CLIENT_ID = "INSERT_CLIENT_ID"

# text coloring constants
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
R = '\033[91m'  # red
B = '\033[1m'  # bold
U = '\033[4m'  # underline
END = '\033[0m'  # end of coloring

OUTPUT = "groups.json"
LOG = "log.txt"


"""
Get user groups -> get user friends -> check for every group in my groups if any of my friends is a member
of this group -> if true, then add this group to the list of the common groups -> calculate difference between
user groups and common groups -> fetch and print info on these groups -> write the info down to a file
"""


def main(chunk_size):
    # chunk is the amount of IDs sent with every request in find_common()
    if not chunk_size:
        chunk_size = 50

    clear_screen()
    display_title()

    # retrieve user info
    user = input(f"{Y}Enter user ID or a screen name:{END}\n")
    print(f"\n{Y}Retrieving user info...{END}\n")
    sleep(1)

    user_groups, user_friends = fetch_user_info(user)

    # fetch common groups
    print(f"\n{Y}Fetching common groups...{END}")
    sleep(2)
    print(f"{B}Status:{END} {Y}In progress{END}\n")
    sleep(1)

    common_groups = find_common(user_groups, user_friends, chunk_size)

    print(f"\n\n{B}Status:{END} {G}Successful{END}\n")
    sleep(2)

    # find uncommon groups
    print(f"{Y}Calculating difference...{END}")
    sleep(1)

    uncommon_groups = set(user_groups) - set(common_groups)

    print(f"{G}UNCOMMON GROUPS FOUND: {len(uncommon_groups)}{END}\n")
    sleep(2)

    # fetch uncommon groups info
    print(f"{Y}Fetching uncommon groups info...{END}")
    sleep(2)
    print(f"{B}Status:{END} {Y}In progress{END}\n")
    sleep(1)

    uncommon_groups_info = fetch_uncommon_info(uncommon_groups)

    print(f"\n\n{B}Status:{END} {G}Successful{END}\n")
    sleep(2)

    # display retrieved info and write it to a JSON file
    print_and_write(uncommon_groups_info)

    print(f"{B}The data has been written to {os.getcwd()}\\{OUTPUT}{END}")
    sleep(1)

    print(f"\n{Y}END OF PROGRAM{END}")


def authorize(discard_token):
    """
    Either opens a saved token file to be used in requests or calls get_token()
    to obtain a new one.
    @return: Dictionary of authorization parameters
    """

    clear_screen()

    print(f"{Y}Authorization...\n{END}")
    sleep(1)

    try:
        # checks if the token was saved more that 23h 50m ago
        if time() - os.stat("token.dat").st_mtime < 85800:
            with open("token.dat", "rb") as f:
                data = pickle.load(f)
            print(f"{G}AUTHORIZED FROM A SAVED TOKEN{END}")
            sleep(2)

            return {"v": 5.103, "access_token": data}
        else:
            return get_token(discard_token)
    except FileNotFoundError:
        return get_token(discard_token)


def clear_screen():
    """
    Clears console screen and turns on color support (the latter is only for Win).
    """

    if sys.platform == "win32":
        os.system("cls")
        os.system("color")
    elif sys.platform == "linux":
        os.system("clear")


def display_title():
    """
    Displays a fancy title screen. :)
    """

    print("\n")
    print("\t\t********************************************************")
    print("\t\t***                    Spy Game                      ***")
    print("\t\t***      Course work for Netology Python course      ***")
    print("\t\t***               By Roman Vlasenko                  ***")
    print("\t\t********************************************************")

    print(f"\n{U}Goal: Find and print every VK group which member the user is, but his friends are not.{END}\n")


def fetch_uncommon_info(uncommon_groups):
    """
    Retrieves information about user groups, which don't have any of the user's friends for a member.

    @param uncommon_groups: A list of groups IDs
    @return: Dictionary containing a name, an ID and a member's count for every uncommon group
    """

    groups_info = []

    for gindex, group in enumerate(uncommon_groups, start=1):
        sleep(0.2)
        params = dict(**token, group_id=group, fields="members_count")
        # status bar
        print(f"{B}Groups processed: {gindex}/{len(uncommon_groups)}  {END}", end="\r")

        try:
            response = requests.get(API_URL + "/groups.getById", params=params).json()
            assert "response" in response, f"{response['error']['error_msg']}"
        except AssertionError as error:
            print(f"{R}API Error:{END}", error)
        else:
            name, gid, members_count = response["response"][0]["name"], \
                                       response["response"][0]["id"], \
                                       response["response"][0].get("members_count", "Unavailable")

            groups_info.append({"name": name, "gid": gid, "members_count": members_count})

    return groups_info


def fetch_user_info(user):
    """
    Sends a request to the API to obtain user info: name, id,
    list of friends and list of groups. Prints out user's name and ID.

    @param user: User's ID or a screen name from input
    @return: List of user friends IDs, list of user groups IDs
    """

    code = """
    var user = API.users.get({"user_ids": """+f'"{user}"'+"""});
    var user_id = user[0].id;
    var name = user[0].first_name + " " + user[0].last_name;
    var groups = API.groups.get({"user_id": user_id}).items;
    var friends = API.friends.get({"user_id": user_id}).items;

    return {"user_name": name, "user_id": user_id, "friends_ids": friends, "groups_ids": groups};"""
    # request user info using VKScript code above
    try:
        response = requests.get(API_URL + "/execute", params=dict(**token, code=code)).json()
        assert "response" in response, f"{response['error']['error_msg']}"
    except AssertionError as error:
        print(f"{R}API Error:{END}", error)
        quit()
    else:
        user_name, user_id, user_friends, user_groups = response["response"].values()

        print(B + f"Name: {user_name}" + END)
        print(B + f"ID: {user_id}" + END)
        sleep(2)

        return user_groups, user_friends


def find_common(user_groups, user_friends, amount):
    """
    For every group from the user groups list, ckecks if any of the user's friends is a member the group.
    If true, appends this group to a list of common groups.

    @param user_groups: List of user groups IDs
    @param user_friends: List of user friends IDs
    @param amount: Amount of friends IDs which will be sent with every request to the API method
    @return: List of common groups IDs
    """

    common_groups = []

    for gindex, group in enumerate(user_groups, start=1):
        processed = 0
        for friends_chunk in get_chunk(user_friends, amount):
            sleep(0.2)
            # "user_ids" parameters must be a list of comma-separated numbers
            user_ids = ",".join([str(friend) for friend in friends_chunk])
            payload = dict(**token, group_id=group, user_ids=user_ids)
            # status bar
            processed += len(friends_chunk)
            print(f"{B}Group {gindex}/{len(user_groups)}, "
                  f"friends processed: {processed}/{len(user_friends)}  {END}", end="\r")

            try:
                response = requests.post(API_URL + "/groups.isMember", data=payload).json()
                assert "response" in response, (f"{response['error']['error_msg']}", response["error"])
            except AssertionError as error:
                print(f"{R}API Error: {END}", error.args[0][0])
                log.append(error.args[0][1])
            else:
                # if any friend in the chunk is a member, add the group to a list
                # and get to the next chunk of friends
                for response in response["response"]:
                    if response["member"]:
                        common_groups.append(group)
                        break

    return common_groups


def get_chunk(friendlist, amount):
    """
    Splits list of user friends IDs in chunks, each to be sent to groups.isMember method
    by the find_common() function ("user_ids" field).

    @param friendlist: List of friends IDs
    @param amount: Aomunt of items the chunk (50 by default, could be changed with a command line argument)
    """

    for index in range(0, len(friendlist), amount):
        yield friendlist[index:index + amount]


def get_token(discard_token):
    """
    Establishes an OAuth2 session to retrieve a token for further API requests.
    Saves retrieved token to a file unless a command line argument "--discard_token" is given
    @return: Dictionary of authorization parameters
    """

    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID), redirect_uri=REDIRECT_URI,
                       scope="friends, groups") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL)
        webbrowser.open_new_tab(authorization_url)
        vk_response = input("Enter VK token response:\n").rstrip()
        vk.token_from_fragment(vk_response)

    if not discard_token:
        with open("token.dat", "wb") as f:
            pickle.dump(vk.access_token, f)

    return {"v": 5.103, "access_token": vk.access_token}


def logger(errors):
    """
    Creates a log file at the end of the program.
    @param errors: List of dictionaries, containing error information returned from the API
    """
    if len(errors) < 1:
        errors.append("No errors occured during the execution")
    with open(LOG, "w", encoding="utf-8") as f:
        for error in errors:
            json.dump(error, f, indent=2)
            f.write("\n")


def parse_arguments():
    """
    Parses command line arguments using argparse module.
    @return: Amount of friends IDs which will be sent with every request to the API method in find_common()
    @return: Boolean value to switch off token pickling option in get_token()
    @return: Boolean value to switch on log writing option (see logger())
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--chunk_size",
                        help="amount of friends checked for membership with every API request, max. 500",
                        type=int)
    parser.add_argument("-t", "--discard_token",
                        help="don't save the token to a file",
                        action="store_true")
    parser.add_argument("-d", "--debug",
                        help="generate log file at the termination",
                        action="store_true")
    args = parser.parse_args()

    return args.chunk_size, args.discard_token, args.debug


def print_and_write(groups_info):
    """
    Prints out uncommon groups information and writes this data to a JSON file.

    @param groups_info: Dictionary of groups info
    """

    for group in groups_info:
        print(f"{B}Group name: {group['name']}{END}")
        print(f"{B}Group ID: {group['gid']}{END}")
        print(f"{B}Members count: {group['members_count']}\n{END}")
        sleep(0.2)

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump(groups_info, file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    log = []

    chunk, cache, debug = parse_arguments()
    token = authorize(cache)
    main(chunk)

    if debug:
        logger(log)
        print(f"\n{B}Log file has been saved to {os.getcwd()}\\{LOG}{END}")
