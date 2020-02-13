from netology_projects.vkinder.user import User


class Match(User):

    def __init__(self, info, personal, interest, groups):
        super().__init__(info, personal, interest, groups)
        self.common_friends = None
        self.score = 300  # base score

    def __repr__(self):
        return f'Match {self.name} {self.surname} {self.age}'

