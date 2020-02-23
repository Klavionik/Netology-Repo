import json
import os
import unittest
from unittest.mock import patch, MagicMock

from vkinder import app as vkinder
from vkinder.db import User as UserTable, \
    Match as MatchTable, Photo, db_session
from vkinder.globals import root
from vkinder.types import User

fixtures_path = os.path.join(root, 'tests', 'fixtures')
db_path = f'sqlite:///{os.path.join(fixtures_path, "test.db")}'
mock_print = MagicMock()


@patch('builtins.print', mock_print)
class NewUserTest(unittest.TestCase):
    app = vkinder.App('test_id',
                      'test_token',
                      output_amount=10,
                      refresh=False,
                      db=db_path)

    with open(f"{os.path.join(fixtures_path, 'user.json')}") as f:
        user = json.load(f)

    with open(f"{os.path.join(fixtures_path, 'groups.json')}", encoding='utf8') as f:
        groups = json.load(f)

    @classmethod
    def tearDownClass(cls) -> None:
        with db_session(cls.app.db.factory) as session:
            lindsey = session.query(UserTable).filter(UserTable.uid == cls.user[0]['id']).one()
            session.delete(lindsey)
        del cls.app

    @patch('vkinder.app.App._fetch_user_groups')
    @patch('vkinder.app.App._fetch_user')
    def test_new_user_from_api(self, mock_fetch_user, mock_fetch_user_groups):
        mock_fetch_user.return_value = (self.user[0]['id'], self.user[0])
        mock_fetch_user_groups.return_value = self.groups

        self.app.new_user(self.user[0]['id'])

        self.assertIsNotNone(self.app.current_user,
                             'User fetched from API and assigned to the class attribute')
        self.assertIsInstance(self.app.current_user, User,
                              'App assigned a :class:`User` instance')
        self.assertEqual(self.app.current_user.uid, self.user[0]['id'],
                         'A :class:`User` instance uid matches test user id')

    @patch('vkinder.app.App._fetch_user')
    def test_new_user_from_database(self, mock_fetch_user):
        mock_fetch_user.return_value = (1, None)

        self.app.new_user(1)

        self.assertIsNotNone(self.app.current_user,
                             'User loaded and assigned to the class attribute')
        self.assertIsInstance(self.app.current_user, User,
                              'App assigned a :class:`User` instance')
        self.assertEqual(self.app.current_user.uid, 1,
                         'A :class:`User` instance uid matches test user id')


@patch('builtins.print', mock_print)
class SpawnMatchesTest(unittest.TestCase):
    app = vkinder.App('test_id',
                      'test_token',
                      output_amount=10,
                      refresh=False,
                      db=db_path)

    with open(f"{os.path.join(fixtures_path, 'matches.json')}", encoding='utf8') as f:
        matches = json.load(f)

    @classmethod
    def tearDownClass(cls) -> None:
        with db_session(cls.app.db.factory) as session:
            session.query(MatchTable).filter(MatchTable.uid > 20).delete()
            session.query(Photo).filter(Photo.id > 20).delete()
        del cls.app

    @patch('vkinder.app.App._fetch_user')
    @patch('vkinder.app.App._prepare_matches')
    def test_spawn_matches(self, mock_prepare_matches, mock_fetch_user):
        matches_length = len(self.matches['matches_info'])
        mock_prepare_matches.return_value = (self.matches['matches_info'],
                                             self.matches['matches_groups'],
                                             self.matches['matches_photos'])
        mock_fetch_user.return_value = (1, None)

        self.assertFalse(self.app.spawn_matches(),
                         'Returns False if no user set')
        self.app.new_user(1)
        self.assertEqual(self.app.spawn_matches(), matches_length,
                         'Returns number of found matches')
        self.assertEqual(matches_length, len(self.app.matches),
                         'All found matches assigned to the class attribute')


if __name__ == '__main__':
    unittest.main()
