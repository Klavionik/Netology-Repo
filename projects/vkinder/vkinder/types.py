import pickle
from datetime import datetime

from .api import get_cities
from .globals import *
from .utils import cleanup, common, verify_bday, flatten, sex


class User:

    def __init__(self, general, personal, interests, groups):
        self.uid = general['uid']
        self.name = general['name']
        self.surname = general['surname']
        self.sex = general['sex']
        self.age = general['age']
        self.city = general['city']
        self.interests = interests
        self.personal = personal
        self.groups = tuple(groups)

    @classmethod
    def from_api(cls, info, groups, *args, **kwargs):
        general, personal, interests = cls.parse(info)
        return cls(general, personal, interests, groups)

    @classmethod
    def from_database(cls, db_user):
        general = {}
        for _, cls_attr in user_map['general'].items():
            general[cls_attr] = getattr(db_user, cls_attr)
        interests = pickle.loads(db_user.interests)
        personal = pickle.loads(db_user.personal)
        groups = pickle.loads(db_user.groups)
        return cls(general, personal, interests, groups)

    @classmethod
    def parse(cls, info):
        """
        Takes a VK API `User` object in the form of a dictionary and prepares its contents
        in order to create a :class:`User` object.

        :param info: Dictionary describing a VK API `User` object
        :return: Parsed user profile info
        """
        flat_info = flatten(info)
        bad_value = ''

        parsed_general = {}
        parsed_personal = {}
        parsed_interests = {}

        for category, mapping in user_map.items():
            for vk_field, cls_attr in mapping.items():
                attr = flat_info.get(vk_field, None)
                if vk_field == 'bdate':
                    attr = cls.get_usr_age(attr)
                elif vk_field == 'common_friends':
                    pass  # :class:`User` object actually doesn't need this :\
                elif not attr or attr == bad_value:
                    attr = cls.ask_for_attribute(cls_attr)

                if category == 'personal':
                    parsed_personal[cls_attr] = attr
                elif category == 'interests':
                    parsed_interests[cls_attr] = attr
                else:
                    parsed_general[cls_attr] = attr

        return parsed_general, parsed_personal, parsed_interests

    @classmethod
    def ask_for_attribute(cls, attribute):
        """
        Handles the case, when user information is incomplete and requires clarification.

        :param attribute: Attribute name of :class:`User`
        :return: Attribute's value
        """
        path = os.path.join(resources, 'output', attribute)

        with open(f'{path}.txt', encoding='utf8') as f:
            output = f.read().strip()
        value = input(f'\n{output}\n\n')

        if attribute == 'city':
            city_id = get_cities(value)
            value = city_id['items'][0]['id']

        if isinstance(value, str) and value.isdigit():
            value = int(value)

        return value

    @classmethod
    def get_usr_age(cls, bday):
        """
        Takes the current user's birth date and returns their age.

        :param bday: Birth date formatted as d.m.yyyy
        :return: Exact user age
        """
        if not verify_bday(bday):
            bday = input('\nBirth date is incomplete or incorrect.'
                         '\nPlease, enter your birth date as dd.mm.yyyy\n').rstrip()
        try:
            bday = datetime.strptime(bday, '%d.%m.%Y')
        except ValueError:
            print(f"{Y}Invalid data format. Age set to 18.{END}")
            return 18
        today = datetime.today()
        return today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))

    def search_criteria(self, ignore_city, ignore_age, same_sex):
        age_bound = AGE_BOUND if not ignore_age else 100
        criteria = {'city': 0 if ignore_city else self.city,
                    'sex': sex(self.sex, same_sex),
                    'age_from': self.age - age_bound if (self.age - age_bound) >= 18 else 18,
                    'age_to': self.age + age_bound,
                    'has_photo': 1,
                    'count': 1000,
                    'fields': 'blacklisted,'
                              'blacklisted_by_me,'
                              'relation'}
        return criteria

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'

    def __repr__(self):
        return f'User {self.name} {self.surname}'


class Match(User):

    def __init__(self, general, personal, interest, groups, photos):
        super().__init__(general, personal, interest, groups)
        self.photos = tuple(photos)
        self.common_friends = int(general['common_friends'])
        self.score = 400  # base score
        self.interests_score = 0
        self.personal_score = 0
        self.friends_score = 0
        self.groups_score = 0

    @classmethod
    def from_api(cls, info, groups, *args, **kwargs):
        general, personal, interests = cls.parse(info)
        return cls(general, personal, interests, groups, kwargs['photos'])

    @classmethod
    def parse(cls, info):
        """
        Takes a VK API `User` object in the form of a dictionary and prepares its contents
        in order to create a :class:`Match` object.

        :param info: Dictionary describing a VK API `User` object
        :return: Parsed user profile info
        """
        flat_response = flatten(info)
        bad_value = ''

        parsed_info = {}
        parsed_personal = {}
        parsed_interests = {}

        for category, mapping in match_map.items():
            for vk_field, cls_attr in mapping.items():
                value = flat_response.get(vk_field, None)
                if not value or value == bad_value:
                    value = False
                if vk_field == 'bdate':
                    if not verify_bday(value):
                        value = 'Unknown'
                    else:
                        value = cls.get_usr_age(value)

                if category == 'personal':
                    parsed_personal[cls_attr] = value
                elif category == 'interests':
                    parsed_interests[cls_attr] = value
                else:
                    parsed_info[cls_attr] = value

        return parsed_info, parsed_personal, parsed_interests

    @property
    def total_score(self):
        return self.score + self.interests_score + \
               self.personal_score + self.friends_score + \
               self.groups_score

    @property
    def profile(self):
        return f"https://vk.com/id{self.uid}"

    def __repr__(self):
        return f'Match {self.name} {self.surname} {self.age}'

    def scoring(self, model):
        self.interests_score = self._score_interests(model)
        self.personal_score = self._score_personal(model)
        self.friends_score = self._score_friends()
        self.groups_score = self._score_groups(model)

    def _score_interests(self, model):
        interests_score = 0

        for field in model.interests:
            user_value = model.interests[field]
            match_value = self.interests.get(field, None)
            if match_value:
                clean_user_interest = cleanup(user_value)
                clean_match_interest = cleanup(match_value)
                field_score = INTERESTS_FACTOR * common(clean_match_interest, clean_user_interest)
                interests_score += field_score
        return interests_score

    def _score_personal(self, model):
        personal_score = 0

        for field in model.personal:
            user_value = model.personal[field]
            match_value = self.personal.get(field, None)
            if match_value == user_value:
                personal_score += PERSONAL_FACTOR * 1
        return personal_score

    def _score_friends(self):
        friends_score = 0

        friends_score += FRIENDS_FACTOR * self.common_friends

        return friends_score

    def _score_groups(self, model):
        groups_score = 0

        groups_score += GROUPS_FACTOR * common(self.groups, model.groups)

        return groups_score

    def search_criteria(self, ignore_city, ignore_age, same_sex):
        pass

    @classmethod
    def from_database(cls, db_user):
        pass

    @classmethod
    def ask_for_attribute(cls, attribute):
        pass
