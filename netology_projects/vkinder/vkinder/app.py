import json
from time import sleep

import vkinder.api as api
import vkinder.utils as utils
from vkinder.auth import authorize
from vkinder.db import AppDB, db_session
from vkinder.globals import *
from vkinder.types import User, Match


class App:

    def __init__(self, owner_id, token, output_amount, refresh):
        """
        Initializes an instance of the VKInder app.

        :param owner_id: id of the app owner (i.e. the person, who's running the app)
        :param token: VK API token of the app owner
        """
        self.owner = owner_id
        self.token = token
        self.api = API_URL
        self.v = VERSION
        self.auth = {'v': self.v, 'access_token': self.token}
        self.db = AppDB(dbpath)
        self.refresh = refresh
        self.output_amount = output_amount
        self.req_fields = 'bdate,city,sex,common_count,' \
                          'games,music,movies,interests,tv,books,personal'

        self.current_user = None
        self.matches = None

    def new_user(self, target):
        """
        Collects all required data from the VK API and user input and creates a User object
        (representing the current user, i.e. the person looking for a match).

        Loads user from the database if found,

        :param target: target user id
        :return: :class:`User` object
        """
        target_id, target_info = self._fetch_user(target)

        with db_session(self.db.factory) as session:
            user_from_db = self.db.get_user(target_id, session)
            if user_from_db and not self.refresh:
                user = User.from_database(user_from_db)
                self.current_user = user
                print(f'\n{G}{user} loaded from the database.{END}')
            else:
                target_groups = self._fetch_user_groups(target_id)
                user = User.from_api(target_info, target_groups)
                self.current_user = user
                self.db.add_user(user, session)
                print(f'\n{G}{user} loaded from the API{END}')

        return str(self.current_user)

    def spawn_matches(self):
        """
        Creates a list of :class:`Match` objects using the information acquired
        from the VK API and processed by the application. Adds every match to the database.

        :return: list of :class:`Match` objects
        """

        if self.current_user:

            matches_info, matches_groups, matches_photos = self._prepare_matches()

            matches = []

            bar = utils.progress_bar("Building matches: ")

            for match_info, match_groups, match_photos in \
                    bar(zip(matches_info, matches_groups, matches_photos),
                        max_value=len(matches_info)):
                top3_photos = self._get_top3_photos(match_photos)
                match_object = Match.from_api(match_info, match_groups, photos=top3_photos)
                match_object.scoring(self.current_user)
                matches.append(match_object)

                with db_session(self.db.factory) as session:
                    self.db.add_match(match_object, top3_photos, self.current_user.uid, session)

            self.matches = matches

            return len(self.matches)

        else:
            return False

    def list_users(self):

        with db_session(self.db.factory) as session:
            users_list = self.db.get_all_users(session)
            for user in users_list:
                print(f'{G}{user.name} {user.surname} Age {user.age} ID {user.uid}{END}')

    def next_match(self, user_id):

        with db_session(self.db.factory) as session:
            user = self.db.get_user(user_id, session)
            if user:
                top10_matches = self.db.pop_match(user_id, AMOUNT, session)
            else:
                return False

        path = os.path.join(data, f'{user_id}_matches.json')
        with open(path, 'w', encoding='utf8') as f:
            json.dump(top10_matches, f, indent=2)

            return len(top10_matches)

    def _fetch_user(self, identificator):
        api_response = api.users_get(self.auth,
                                     user_ids=identificator,
                                     fields=self.req_fields)
        user_info = api_response[0]
        target_id = user_info['id']

        return target_id, user_info

    def _fetch_user_groups(self, user_id):

        user_groups = api.groups_get(self.auth, user_id=user_id)
        return user_groups['items']

    def _prepare_matches(self):
        """
        Coordinates acquiring and processing matches profiles in order to spawn
        :class:`Match` objects.

        :return: tuple of lists
        """

        match_search_criteria = self.current_user.search_criteria
        possible_matches = self._get_possible_matches(match_search_criteria)

        matches_ids = self._get_matches_ids(possible_matches)
        matches_info = api.users_get(self.auth,
                                     user_ids=matches_ids,
                                     fields=self.req_fields)
        matches_groups, matches_photos = self._get_matches_groups_photos(matches_ids)

        return matches_info, matches_groups, matches_photos

    def _get_possible_matches(self, search_criteria):
        """
        Acquires VK user profiles matching the current user profile based on
        sex, age range and city of residence.

        :param search_criteria: dictionary of request parameters
        :return: list of dictionaries, each describing a VK API `User` object
        """
        possible_matches = api.users_search(self.auth, search_criteria)['items']

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

        :param matches_items: list of VK `User` objects
        :return: list of matches ids
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
        variables in that code and returns it ready to be sent to the `execute` method.

        :param ids: list of possible matches ids
        :return: string containing VKScript code
        """
        path = os.path.join(resources, 'vkscript.txt')

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

        :param matches_ids: list of matches ids
        :return: tuple of dicts (matches groups, matches photos)
        """
        matches_groups = []
        matches_photos = []

        bar = utils.progress_bar('Fetching profiles: ')

        for ids_chunk in bar(utils.next_ids(matches_ids),
                             max_value=len(matches_ids) / 12):
            code = self._prepare_code(ids_chunk)
            result = api.execute(self.auth, code=code)
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

        :param photos: list of all photos for a match
        :return: list of top-3 photos for a match
        """
        photos_processed = []

        for photo in photos:
            photo_processed = {'likes': photo['likes']['count'],
                               'link': utils.find_largest_photo(photo['sizes'])}
            photos_processed.append(photo_processed)

        return sorted(photos_processed, key=lambda x: x['likes'], reverse=True)[:3]


def startup():
    try:
        os.mkdir(data)
    except FileExistsError:
        pass

    owner_token, app_owner = authorize(SAVE)

    return App(app_owner, owner_token, AMOUNT, REFRESH)
