"""
VKInder: a coursework for Netology Python course by Roman Vlasenko

"""

from time import sleep
import netology_projects.vkinder.vkinder.api as api
import netology_projects.vkinder.vkinder.utils as utils
from netology_projects.vkinder.vkinder.auth import authorize
from netology_projects.vkinder.vkinder.globals import *
from netology_projects.vkinder.vkinder.types import User, Match
from netology_projects.vkinder.vkinder.db import VKinderDB


class App:

    def __init__(self, owner_id, token, target=None):
        """
        Initializes an instance of the VKInder app.

        :param owner_id: id of the app owner (i.e. the person, who's running the app)
        :param token: VK API token of the app owner
        :param target: target user id or screenname
        """
        self.owner = owner_id
        self.token = token
        self.api = API_URL
        self.v = VERSION
        self.auth = {'v': self.v, 'access_token': self.token}
        self.db = VKinderDB(dbpath)

        if not target:
            target = input("Let's find somebody's fortune! "
                           "But first, enter their ID or screenname below.\n")

        self.current_user = self._set_user(target)
        self.matches = self._spawn_matches()

    def _set_user(self, target):
        """
        Collects all required data from the VK API and user input and creates a User object
        (representing the current user, i.e. the person looking for a match).

        :param target: target user id or screenname
        :return: :class:`User` object
        """
        user_info = api.users_get(self.auth, user_ids=target, fields=req_fields)
        target_id = user_info[0]['id']

        user_groups = api.groups_get(self.auth, user_id=target_id)['items']
        info, personal, interests = self._parse_user(user_info[0])
        user = User(info, personal, interests, user_groups)

        self.db.add_user(user)
        return user

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
        matches_ids = [match['id'] for match in matches_items
                       if (not match['blacklisted']) and
                       (not match['blacklisted_by_me']) and
                       (match.get('relation', 0) not in (2, 3, 4, 7, 8)) and
                       not match['is_closed']]

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

    def _get_possible_matches(self, search_criteria):
        """
        Acquires VK user profiles matching the current user profile based on
        sex, age range and city of residence.

        :param search_criteria: dictionary of request parameters
        :return: list of dictionaries, each describing a VK API `User` object
        """
        possible_matches = api.users_search(self.auth, search_criteria)['items']

        return possible_matches

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

        for ids_chunk in utils.next_ids(matches_ids):
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

    def _prepare_matches(self):
        """
        Coordinates acquiring and processing matches profiles in order to spawn
        :class:`Match` objects.

        :return: tuple of lists
        """
        match_search_criteria = self.current_user.search_criteria
        possible_matches = self._get_possible_matches(match_search_criteria)

        matches_ids = self._get_matches_ids(possible_matches)
        matches_info = api.users_get(self.auth, user_ids=matches_ids, fields=req_fields)
        matches_groups, matches_photos = self._get_matches_groups_photos(matches_ids)

        return matches_info, matches_groups, matches_photos

    def _spawn_matches(self):
        """
        Creates a list of :class:`Match` objects using the information acquired
        from the VK API and processed by the application. Adds every match to the database.

        :return: list of :class:`Match` objects
        """

        print("Please, wait a minute while we're collecting data\n")

        matches_info, matches_groups, matches_photos = self._prepare_matches()

        matches = []

        for match_info, match_groups, match_photos in \
                zip(matches_info, matches_groups, matches_photos):
            info, personal, interests = self._parse_match(match_info)
            top3_photos = self._get_top3_photos(match_photos)
            match_object = Match(info, personal, interests, match_groups, top3_photos)
            match_object.scoring(self.current_user)
            matches.append(match_object)

            self.db.add_match(match_object, top3_photos, self.current_user.uid)

        print(f'{len(matches)} matches found!\n')

        return matches

    def _parse_user(self, info):
        """
        Takes a VK API `User` object in the form of a dictionary and prepare its contents
        in order to create a :class:`User` object.

        :param info: dictionary describing a VK API `User` object
        :return: tuple of dicts (general profile info, personal info, interests info)
        """
        flat_info = utils.flatten(info)
        bad_value = ''

        parsed_general = {}
        parsed_personal = {}
        parsed_interests = {}

        for vk_field, cls_attr in user_attr_map.items():
            attr = flat_info.get(vk_field, None)
            if not attr or attr == bad_value:
                attr = self._ask_for_attribute(cls_attr)
            if vk_field == 'bdate':
                attr = utils.get_usr_age(attr)

            if cls_attr.startswith('personal.'):
                parsed_personal[cls_attr] = attr
            elif cls_attr.startswith('interests.'):
                parsed_interests[cls_attr] = attr
            else:
                parsed_general[cls_attr] = attr

        return parsed_general, parsed_personal, parsed_interests

    @staticmethod
    def _parse_match(info):
        """
        Takes a VK API `User` object in the form of a dictionary and prepares its contents
        in order to create a :class:`Match` object.

        :param info: dictionary describing a VK API `User` object
        :return: tuple of dicts (general profile info, personal info, interests info)
        """
        flat_response = utils.flatten(info)
        bad_value = ''

        parsed_info = {}
        parsed_personal = {}
        parsed_interests = {}

        for vk_field, cls_attr in match_attr_map.items():
            value = flat_response.get(vk_field, None)
            if not value or value == bad_value:
                value = None
            if vk_field == 'bdate':
                if not utils.verify_bday(value):
                    value = 'Unknown'
                else:
                    value = utils.get_usr_age(value)

            if cls_attr.startswith('personal.'):
                parsed_personal[cls_attr] = value
            elif cls_attr.startswith('interests.'):
                parsed_interests[cls_attr] = value
            else:
                parsed_info[cls_attr] = value

        return parsed_info, parsed_personal, parsed_interests

    def _ask_for_attribute(self, attribute):
        """
        Handles the case, when user information is incomplete and requires clarification.
        Displays an appropriate message, prompts for an input.

        If given attribute value is a city name, sends a request to the VK API `database.getCities`
        method in order to get a city id.

        :param attribute: attribute of :class:`User`
        :return: attribute's value
        """
        path = os.path.join(resources, 'output', attribute)
        output = open(f'{path}.txt', encoding='utf8').read()
        value = input(f'\n{output}\n\n')

        if attribute == 'city':
            city_id = api.get_cities(self.auth, value)
            value = city_id['items'][0]['id']

        if isinstance(value, str) and value.isdigit():
            value = int(value)

        return value


def startup():
    try:
        os.mkdir(data)
    except FileExistsError:
        pass
    print(__doc__)


if __name__ == '__main__':
    startup()

    app_token, app_owner = authorize()

    app = App(app_owner, app_token)
