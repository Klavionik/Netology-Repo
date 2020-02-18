from collections import namedtuple
from netology_projects.vkinder.vkinder.globals import AGE_BOUND, \
    INTERESTS_FACTOR, PERSONAL_FACTOR, FRIENDS_FACTOR, GROUPS_FACTOR
from netology_projects.vkinder.vkinder.utils import cleanup, common


class User:

    def __init__(self, info, personal, interests, groups):
        self.uid = None
        self.name = None
        self.surname = None
        self.sex = None
        self.age = None
        self.city = None
        self.interests = None
        self.personal = None
        self.groups = None

        self._set_info(info)
        self._set_interests(interests)
        self._set_personal(personal)
        self._set_groups(groups)

    def _set_info(self, info):
        for field in info:
            if hasattr(self, field):
                setattr(self, field, info[field])

    def _set_interests(self, intrs):
        self.interests = namedtuple('Interests',
                                    'interests books games movies music tv')
        for field in self.interests._fields:
            setattr(self.interests, field, intrs[f'interests.{field}'])

    def _set_personal(self, pers):
        self.personal = namedtuple('Personal',
                                   'political religion people_main life_main smoking alcohol')
        for field in self.personal._fields:
            setattr(self.personal, field, pers[f'personal.{field}'])

    def _set_groups(self, groups):
        self.groups = tuple(groups)

    @property
    def search_criteria(self):
        criteria = {'city': self.city,
                    'sex': 1 if self.sex == 2 else 2,
                    'age_from': self.age - AGE_BOUND if (self.age - AGE_BOUND) >= 18 else 18,
                    'age_to': self.age + AGE_BOUND,
                    'has_photo': 1,
                    'count': 1000,
                    'fields': 'blacklisted,'
                              'blacklisted_by_me,'
                              'relation'}
        return criteria

    def __repr__(self):
        return f'User {self.name} {self.surname}'


class Match(User):

    def __init__(self, info, personal, interest, groups, photos):
        super().__init__(info, personal, interest, groups)
        self.photos = None
        self.common_friends = 0
        self.score = 400  # base score
        self.interests_score = 0
        self.personal_score = 0
        self.friends_score = 0
        self.groups_score = 0

        self._set_photos(photos)

    def _set_photos(self, photos):
        self.photos = tuple(photos)

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

        for field in model.interests._fields:
            user_field = getattr(model.interests, field)
            match_field = getattr(self.interests, field)
            if match_field:
                clean_user_interest = cleanup(user_field)
                clean_match_interest = cleanup(match_field)
                field_score = INTERESTS_FACTOR * common(clean_match_interest, clean_user_interest)
                interests_score += field_score
        return interests_score

    def _score_personal(self, model):
        personal_score = 0

        for field in model.personal._fields:
            user_field = getattr(model.personal, field)
            match_field = getattr(self.personal, field)
            if match_field == user_field:
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

    def search_criteria(self):
        pass
