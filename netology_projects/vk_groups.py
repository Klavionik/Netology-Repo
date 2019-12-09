import requests
import json
import os
import sys
import webbrowser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient
from time import sleep

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


"""
Get user groups -> get user friends -> check for every group in my groups if any of my friends is a member
of this group -> if true, then add this group to the list of the common groups -> calculate difference between
user groups and common groups -> fetch and print info on these groups -> write the info down to a file
"""


def main(chunk=50):
    # chunk is the amount of IDs sent with
    # groups.isMember method request in find_common()

    if sys.platform == "win32":
        os.system("cls")
        os.system("color")
    elif sys.platform == "linux":
        os.system("clear")

    if len(sys.argv) > 1:
        chunk = int(sys.argv[1])

    display_title()

    user = input(Y + "Enter user ID or a screen name:\n" + END)

    user_groups, user_friends = retrieve_user_info(user)

    uncommon_groups = find_common(user_groups, user_friends, chunk)

    uncommon_groups_info = find_uncommon(user_groups, uncommon_groups)

    display_result(uncommon_groups_info)

    write_result(uncommon_groups_info)

    print(Y + "\nEND OF PROGRAM" + END)


def authorize():
    with OAuth2Session(client=MobileApplicationClient(client_id=CLIENT_ID), redirect_uri=REDIRECT_URI,
                       scope="friends") as vk:
        authorization_url, state = vk.authorization_url(AUTHORIZE_URL)
        webbrowser.open_new_tab(authorization_url)
        vk_response = input("Enter VK token response:\n").rstrip()
        vk.token_from_fragment(vk_response)

        return {"v": 5.103, "access_token": vk.access_token}


def display_title():
    print("\n")
    print("\t\t********************************************************")
    print("\t\t***                    Spy Game                      ***")
    print("\t\t***      Course work for Netology Python course      ***")
    print("\t\t***               By Roman Vlasenko                  ***")
    print("\t\t********************************************************")

    print(U + "\nGoal: Find and print every VK group which member the user is, but his friends are not.\n" + END)


def retrieve_user_info(user):
    print(Y + "\nRetrieving user info...\n" + END)
    sleep(1)
    # retrieve user's id
    user_info = requests.get(API_URL + "/users.get", params=dict(**token, user_ids=user)).json()
    user_id = user_info["response"][0]["id"]
    name = user_info["response"][0]["first_name"] + " " + user_info["response"][0]["last_name"]

    # print out user info
    print(B + f"Name: {name}" + END)
    print(B + f"ID: {user_id}" + END)
    sleep(3)

    # fetch user's groups
    get_user_groups = requests.get(API_URL + "/groups.get", params=dict(**token, user_id=user_id)).json()

    user_groups = get_user_groups["response"]["items"]

    # fetch user's friends
    get_user_friends = requests.get(API_URL + "/friends.get", params=dict(**token, user_id=user_id)).json()

    user_friends = get_user_friends["response"]["items"]

    return user_groups, user_friends


def get_chunk(friendlist, amount):
    for index in range(0, len(friendlist), amount):
        yield friendlist[index:index + amount]


def find_common(user_groups, user_friends, chunk):
    # fetch common groups
    common_groups = []
    print(Y + "\nFetching common groups..." + END)
    sleep(2)
    print(f"{B}Status:{END} {Y}In progress{END}\n")
    sleep(1)
    for gindex, group in enumerate(user_groups, start=1):
        processed = 0
        for friends_chunk in get_chunk(user_friends, chunk):
            processed += len(friends_chunk)
            user_ids = ",".join([str(f) for f in friends_chunk])
            print(B + f"Group {gindex}/{len(user_groups)}, friends processed {processed}/{len(user_friends)}  " + END, end="\r")
            sleep(0.2)
            try:
                common_response = requests.get(API_URL + "/groups.isMember",
                                               params=dict(**token, group_id=group, user_ids=user_ids)).json()
                assert "response" in common_response, f"{common_response['error']['error_msg']}"
            except AssertionError as error:
                print(R + "API returned an error: " + END, error)
            else:
                for response in common_response["response"]:
                    if response["member"]:
                        common_groups.append(group)
                        break

    print(f"\n\n{B}Status:{END} {G}Successful{END}\n")
    sleep(2)

    return common_groups


def find_uncommon(user_groups, common_groups):
    groups_info = []

    # calculate uncommon groups
    uncommon_groups = set(user_groups) - set(common_groups)

    # fetch uncommon groups info
    print(Y + "Fetching uncommon groups info..." + END)
    sleep(1)
    print(f"{B}Status:{END} {Y}In progress{END}")
    for group in uncommon_groups:
        sleep(0.2)
        try:
            info = requests.get(API_URL + "/groups.getById",
                                params=dict(**token, group_id=group, fields="members_count")).json()
            assert "response" in info, f"{info['error']['error_msg']}"
        except AssertionError as error:
            print(R + "API returned an error: " + END, error)
        else:
            name, gid, members_count = info["response"][0]["name"], \
                                       info["response"][0]["id"], \
                                       info["response"][0]["members_count"]
            groups_info.append({"name": name, "gid": gid, "members_count": members_count})

    print(f"{B}Status:{END} {G}Successful{END}\n")
    sleep(2)

    return groups_info


def display_result(groups_info):

    print(Y + f"UNCOMMON GROUPS FOUND: {len(groups_info)}\n" + END)

    sleep(1)
    for group in groups_info:
        print(B + f"Group name: {group['name']}" + END)
        print(B + f"Group ID: {group['gid']}" + END)
        print(B + f"Members count: {group['members_count']}\n" + END)
        sleep(0.3)


def write_result(data):
    filename = "groups.json"

    # write uncommon groups info down to json file
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(B + f"The data has been written to {os.getcwd()}\\{filename}" + END)
    sleep(1)


if __name__ == '__main__':

    token = authorize()
    main()
