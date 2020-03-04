import json
import os
import sys
from time import sleep

import vkinder.globals as g
import vkinder.utils as utils
from vkinder.api import VKApi
from .auth import authorize
from .db import AppDB, db_session
from .exceptions import APIError
from .types import User, Match


class App:

    def __init__(self, api, flags, db):
        """
        Initializes an instance of the VKInder app.

        :param api: VK API handler
        """
        self.api = api
        self.db = AppDB(db)
        self.export = flags['export']
        self.output_amount = flags['output_amount']

        self.flags = flags

        self.current_user = None

    def new_user(self, target):
        """
        Collects all required data from the VK API and user input and creates a User object
        (representing the current user, i.e. a person looking for a match).

        :param target: Target user id or screen name
        :return: String representation of :class:`User` object.
        """
        try:
            target_id, target_info = self._fetch_user(target)
        except APIError as e:
            if e.code == (30, 113):
                return False
        else:
            with db_session(self.db.factory) as session:
                user_in_db = self.db.get_user(target_id, session)

                if user_in_db:
                    user = User.from_database(user_in_db)
                    self.current_user = user
                    print(f'\n{g.G}{user} loaded from the database.{g.END}')
                else:
                    target_groups = self._fetch_user_groups(target_id)
                    user = User.from_api(target_info, target_groups)
                    self.current_user = user
                    self.db.add_user(user, session)
                    print(f'\n{g.G}{user} loaded from the API{g.END}')

            return str(self.current_user)

    def delete_user(self, user_uid):
        if self.current_user.uid and self.current_user.uid == user_uid:
            self.current_user = None

        with db_session(self.db.factory) as session:
            if user := self.db.get_user(user_uid, session):
                self.db.delete_user(user, session)
                return True
            return False

    def spawn_matches(self):
        """
        Creates a stream of :class:`Match` objects using the information acquired
        from the VK API and processed by the application. Adds every match to the database.

        :return: Number of found matches
        """

        if self.current_user:

            matches_info, matches_groups, matches_photos = self._prepare_matches()

            bar = utils.progress_bar("Building matches: ")

            for match_info, match_groups, match_photos in \
                    bar(zip(matches_info, matches_groups, matches_photos),
                        max_value=len(matches_info)):
                top3_photos = self._get_top3_photos(match_photos)
                match_object = Match.from_api(match_info, match_groups, photos=top3_photos)
                match_object.scoring(self.current_user)

                with db_session(self.db.factory) as session:
                    if match := self.db.get_match(match_object.uid,
                                                  self.current_user.uid,
                                                  session):
                        self.db.update_match(match, match_object, session)
                    else:
                        self.db.add_match(match_object, self.current_user.uid, session)

            return len(matches_info)

        else:
            return False

    def list_users(self):
        """
        Returns list of all users saved in the database.

        :return: Saved users list or False if no users found.
        """
        with db_session(self.db.factory) as session:
            all_users = self.db.get_all_users(session)
            if all_users:
                return self._make_list(all_users)
            else:
                return False

    def next_matches(self, user_id):
        """
        Exports next `amount` of matches for the user with the `user_id`
        to a JSON file.

        :param user_id: VK user id.
        :return: Number of exported matches or False if no user found.
        """
        with db_session(self.db.factory) as session:
            user = self.db.get_user(user_id, session)
            if user:
                next_matches = self.db.pop_match(user_id, self.output_amount, session)
            else:
                return False

        if self.export:
            path = os.path.join(g.data, f'{user_id}_matches.json')
            with open(path, 'w', encoding='utf8') as f:
                json.dump(next_matches, f, indent=2, ensure_ascii=False)

                return len(next_matches)
        return next_matches

    def _fetch_user(self, identificator):
        fields = ','.join(['bdate', 'city', 'sex',
                           'games', 'music', 'movies', 'interests',
                           'tv', 'books', 'personal'])
        api_response = self.api.users_get(user_ids=identificator,
                                          fields=fields)
        user_info = api_response[0]
        user_id = user_info['id']
        user_city = user_info.get('city', None)

        if not user_city:
            city = input("Looks like we don't know, where you live.\n"
                         "What's your city of residence?")
            city_id = self.api.get_cities(city)['items'][0]['id']
            user_info['city'] = city_id

        if user_info.get('is_closed'):
            raise APIError({'error': {'error_code': 30}})

        return user_id, user_info

    def _fetch_user_groups(self, user_id):

        user_groups = self.api.groups_get(user_id=user_id)
        return user_groups['items']

    def _prepare_matches(self):
        """
        Coordinates acquiring and processing matches profiles in order to spawn
        :class:`Match` objects.

        :return: Prepared matches info
        """

        match_search_criteria = self.current_user.search_criteria(self.flags['ignore_city'],
                                                                  self.flags['ignore_age'],
                                                                  self.flags['same_sex'])
        possible_matches = self._get_possible_matches(match_search_criteria)

        matches_ids = self._get_matches_ids(possible_matches)

        fields = ','.join(['bdate', 'city', 'sex', 'common_count'
                                                   'games', 'music', 'movies', 'interests',
                           'tv', 'books', 'personal'])
        matches_general = self.api.users_get(
            user_ids=matches_ids,
            fields=fields)
        matches_groups, matches_photos = self._get_matches_groups_photos(matches_ids)

        return matches_general, matches_groups, matches_photos

    def _get_possible_matches(self, search_criteria):
        """
        Acquires VK user profiles matching the current user profile based on
        the given criteria.

        :param search_criteria: Search criteria for users.search method
        :return: List of dictionaries, each describing a VK API `User` object.
        """
        possible_matches = self.api.users_search(search_criteria)['items']

        return possible_matches

    @staticmethod
    def _get_matches_ids(matches_items):
        """
        Loops through the list of possible matches and filters out unneeded ones.

        For every match, checks
        1) that the match doesn't have the current user blacklisted
        2) that the match is not in the blacklist of a current user
        3) that the match don't any personal relations
        4) that the match's VK profile is not private

        If all these conditions are met, then the function adds a match id to
        to the final list of matches.

        :param matches_items: List of VK `User` objects.
        :return: List of matches ids.
        """
        bar = utils.progress_bar('Sorting out data: ')

        matches_ids = []

        for match in bar(matches_items, max_value=len(matches_items)):
            if (not match['blacklisted']) and \
                    (not match['blacklisted_by_me']) and \
                    (match.get('relation', 0) not in (2, 3, 4, 7, 8)) and \
                    not match['is_closed']:
                matches_ids.append(match['id'])
                sleep(0.010)

        return matches_ids

    @staticmethod
    def _prepare_code(ids):
        """
        Reads a VKScript code from a text file, replaces `ids` and `count`
        variables in that code and returns the result.

        :param ids: List of matches ids.
        :return: String containing VKScript code.
        """
        path = os.path.join(g.resources, 'vkscript.txt')

        with open(path, encoding='utf8') as f:
            code = f.read()

        return code % (ids, len(ids))

    def _get_matches_groups_photos(self, matches_ids):
        """
        Loops through the list of matches ids and gets groups
        and photos info for every id.

        Due to a limitation set by the VK API you can't make more than
        3 API requests per second. To circumvent this limitation
        the `execute` method of the API is used.

        `Execute` method accepts code written in VKScript format
        and allows that code to make up to 25 requests per one
        `execute` method execution.

        Here we split the list in chucks of 12 ids (as we make 2 requests
        for one `execute` code) and process each chuck separately
        and then concatenate all results in the variables
        `matches_groups` and `matches_photos`.

        :param matches_ids: List of matches ids.
        :return: Tuple of dicts (matches groups, matches photos).
        """
        matches_groups = []
        matches_photos = []

        bar = utils.progress_bar('Fetching profiles: ')

        for ids_chunk in bar(utils.next_ids(matches_ids),
                             max_value=len(matches_ids) / 12):
            code = self._prepare_code(ids_chunk)
            result = self.api.execute(code=code)
            groups, photos = result[0], result[1]
            matches_groups.extend(groups)
            matches_photos.extend(photos)
            sleep(0.2)

        return matches_groups, matches_photos

    @staticmethod
    def _get_top3_photos(photos):
        """
        Takes a list of dicts, each describing a photo of a possible match
        and returns a list of the top-3 most popular photos (based on the amount of likes).

        :param photos: list of all photos for a match.
        :return: list of top-3 photos for a match.
        """
        photos_processed = [{'likes': photo['likes']['count'],
                             'link': utils.find_largest_photo(photo['sizes'])}
                            for photo in photos]

        return sorted(photos_processed, key=lambda photo: photo['likes'], reverse=True)[:3]

    @staticmethod
    def _make_list(db_users_list):
        users_list = [{'name': user.name, 'surname': user.surname,
                       'age': user.age, 'uid': user.uid}
                      for user in db_users_list]

        return users_list


def startup(flags):
    try:
        os.mkdir(g.data)
    except FileExistsError:
        pass

    if sys.platform.startswith('win'):
        os.system('color')

    utils.clean_screen()

    owner_token = authorize()
    api = VKApi(g.API_URL, g.VERSION, owner_token)

    return App(api, flags, g.dbpath)
