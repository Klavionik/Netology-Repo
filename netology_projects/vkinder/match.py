from netology_projects.vkinder.user import User
from netology_projects.vkinder.utils import cleanup, common
from netology_projects.vkinder.globals import *


class Match(User):

    def __init__(self, info, personal, interest, groups, photos):
        super().__init__(info, personal, interest, groups)
        self.photos = None
        self.common_friends = 0
        self.score = 300  # base score
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
                print(match_field, clean_match_interest)
                field_score = interests_factor * common(clean_match_interest, clean_user_interest)
                interests_score += field_score
        return interests_score

    def _score_personal(self, model):
        personal_score = 0

        for field in model.personal._fields:
            user_field = getattr(model.personal, field)
            match_field = getattr(self.personal, field)
            if match_field == user_field:
                personal_score += personal_factor * 1
        return personal_score

    def _score_friends(self):
        friends_score = 0

        friends_score += friends_factor * self.common_friends

        return friends_score

    def _score_groups(self, model):
        groups_score = 0

        groups_score += groups_factor * common(self.groups, model.groups)

        return groups_score

    def search_criteria(self):
        pass






