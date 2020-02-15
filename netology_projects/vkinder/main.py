from time import sleep

import netology_projects.vkinder.api as api
import netology_projects.vkinder.utils as utils
from netology_projects.vkinder.auth import authorize
from netology_projects.vkinder.globals import *
from netology_projects.vkinder.match import Match
from netology_projects.vkinder.user import User

__doc__ = \
    """
VKInder: a coursework for Netology Python course by Roman Vlasenko\n
"""


class App:

    def __init__(self, owner_id, token, target=None):
        """
        Initializes an instance of the VKInder app from a VK user id, a VK API token and a target id or screenname.

        :param owner_id: id of the app owner (i.e. the person, who's running the app)
        :param token: VK API token of the app owner
        :param target: target user id or screenname
        """
        self.owner = owner_id
        self.token = token
        self.api = API_URL
        self.v = VERSION
        self.auth = {'v': self.v, 'access_token': self.token}

        if not target:
            target = input("Let's find somebody's fortune! But first, enter their ID below.\n")

        self.current_user = self._set_user(target)
        self.matches = self._spawn_matches()

    def _set_user(self, target):
        """
        Collects all required data from the VK API and user input and creates a User object.

        :param target: target user id or screenname
        :return: :class:`User` object
        """
        user_info = api.users_get(self.auth, user_ids=target, fields=req_fields)
        target_id = user_info[0]['id']
        user_groups = api.groups_get(self.auth, user_id=target_id)
        info, personal, interests = self._parse_user(user_info[0])
        return User(info, personal, interests, user_groups)

    @staticmethod
    def _get_matches_ids(matches_items):
        """
        Loops through the list of possible matches returned by users.search VK API method.
        For every match item, checks

        1) if the match doesn't have a target user blacklisted
        2) if the match is not in the blacklist of a target user
        3) if the match have any personal relations
        4) if the match's VK profile is closed

        If all these conditions are met, then the function adds a match user id to
        to the list of final matches and returns the list.

        :param matches_items: list of possible matches
        :return: list of final matches ids
        """
        matches_ids = [match['id'] for match in matches_items
                       if (not match['blacklisted']) and
                       (not match['blacklisted_by_me']) and
                       (match.get('relation', 0) not in (2, 3, 4, 7, 8)) and
                       not match['is_closed']]

        return matches_ids

    @staticmethod
    def _prepare_code(ids):
        code = \
            """
            var ids = """ + f'{ids}' + """;
            var count = """ + f'{len(ids)}' + """;
            var index = 0;
            var all_groups = [];
            var all_photos = [];
            var groups = null;
            var photos = null;
            var next = 0;


            while (count > 0) {

                next = ids[index];
                groups = API.groups.get({"user_id": next, "count": 1000}).items;
                photos = API.photos.get({'owner_id': next, 'album_id': -6, 'rev': 1, 'extended': 1}).items;
                all_photos.push(photos);
                all_groups.push(groups);
                count = count - 1;
                index = index + 1;
            };


            return [all_groups, all_photos];
        """

        return code

    def _get_possible_matches(self, search_criteria):
        """
        Sends a request to the VK API to acquire possible matches profle info
        based on the current user profile.

        :param search_criteria: dictionary of request parameters from users.search method
        :return: list of VK API user objects
        """
        possible_matches, _ = \
            api.users_search(self.auth, search_criteria)

        return possible_matches

    def _get_matches_groups_photos(self, matches_ids):
        """
        Loops through a list of final matches ids and gets groups info for all the
        matches.

        Due to a limitation of the VK API you can't make more than 3 API requests per second.
        To circumvent this limitation the `execute` method of the API is used.
        `Execute` method accepts code written in VKScript format and allows that code to make
        up to 25 requests per one `execute` method execution.
        We split matches ids list in chucks of 25 ids and process each chuck separately
        and then concatenate all results in a variable `matches_groups`.

        :param matches_ids: list of final matches ids
        :return: list of final matches groups
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

    def _get_top3_photos(self, photos_array):
        processed_photos = []

        for photo in photos_array:
            processed_photo = {'likes': photo['likes']['count'], 'link': utils.find_largest_photo(photo['sizes'])}
            processed_photos.append(processed_photo)

        return sorted(processed_photos, key=lambda x: x['likes'], reverse=True)[:3]


    def _prepare_matches(self):
        """
        Coordinates acquiring and processing matches profiles in order to spawn
        :class:`Match` objects.

        :return: list of final matches info and list of final matches groups
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
        from the VK API.

        :return: list of :class:`Match` objects
        """

        print("Please, wait a minute while we're collecting data\n")

        matches_info, matches_groups, matches_photos = self._prepare_matches()

        matches = []

        for match_info, match_groups, match_photos in zip(matches_info, matches_groups, matches_photos):
            info, personal, interests = self._parse_match(match_info)
            top3_photos = self._get_top3_photos(match_photos)
            match_object = Match(info, personal, interests, match_groups, top3_photos)
            match_object.scoring(self.current_user)
            matches.append(match_object)

        matches.sort(key=lambda x: x.total_score, reverse=True)

        print(f'{len(matches)} possible matches found!\n')

        return matches

    def _parse_user(self, info):
        """
        Takes a VK API user object in the form of a dictionary and parses its contents
        in order to create a :class:`User` object (i.e. the current user, the one we
        are searching matches for).

        :param info: VK API user object as a dictionary
        :return: dicts of user general profile info, user personal info and user interests info
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
        Takes a VK API user object in the form of a dictionary and parses its contents
        in order to create a :class:`Match` object (i.e. the user, who has profile info
        matching with the current user profile).
        
        :param info: VK API user object as a dictionary
        :return: dicts of match general profile info, match personal info and match interests info
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
        Displays an appropriate message, asks for user input.

        If given attribute value is a city name, sends a request to the VK API `database.getCities`
        method in order to get a city id.

        :param attribute: an attribute of :class:`User`
        :return: an attribute's value
        """
        output_filename = os.path.join(resources, attribute)
        output = open(f'{output_filename}.txt', encoding='utf8').read()
        attr = input(f'\n{output}\n\n')

        if attribute == 'city':
            city_id = api.get_cities(self.auth, attr)
            attr = city_id['items'][0]['id']

        if isinstance(attr, str) and attr.isdigit():
            attr = int(attr)

        return attr


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

    y = 1