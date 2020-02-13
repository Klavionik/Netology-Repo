from netology_projects.vkinder.globals import *


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
        self.interests = namedtuple('Interests', 'interests books games movies music tv')
        for field in self.interests._fields:
            setattr(self.interests, field, intrs[f'interests.{field}'])

    def _set_personal(self, pers):
        self.personal = namedtuple('Personal', 'political religion people_main life_main smoking alcohol')
        for field in self.personal._fields:
            setattr(self.personal, field, pers[f'personal.{field}'])

    def _set_groups(self, groups):
        self.groups = tuple(groups)

    @property
    def search_criteria(self):
        criteria = {'city': self.city,
                    'sex': 1 if self.sex == 2 else 2,
                    'age_from': self.age - age_bound if (self.age - age_bound) >= 18 else 18,
                    'age_to': self.age + age_bound,
                    'has_photo': 1,
                    'count': 1000,
                    'fields': 'blacklisted,'
                              'blacklisted_by_me,'
                              'relation'}
        return criteria

    def __repr__(self):
        return f'User {self.name} {self.surname}'
