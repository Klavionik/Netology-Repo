import json
import os
import unittest
from unittest.mock import patch, MagicMock

from vkinder import app
from vkinder.db import User as UserTable, db_session
from vkinder.globals import root
from vkinder.types import User

fixtures_path = os.path.join(root, 'tests', 'fixtures')
db_path = f'sqlite:///{os.path.join(fixtures_path, "test.db")}'
mock_print = MagicMock()


@patch('builtins.print', mock_print)
class NewUserTest(unittest.TestCase):
    app = app.App('test_id',
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

    @patch('vkinder.app.App._fetch_user_groups')
    @patch('vkinder.app.App._fetch_user')
    def test_new_user_from_api(self, fake_fetch_user, fake_fetch_user_groups):
        fake_fetch_user.return_value = (self.user[0]['id'], self.user[0])
        fake_fetch_user_groups.return_value = self.groups

        self.app.new_user(self.user[0]['id'])

        self.assertIsNotNone(self.app.current_user)
        self.assertIsInstance(self.app.current_user, User)
        self.assertEqual(self.app.current_user.uid, self.user[0]['id'])

    @patch('vkinder.app.App._fetch_user')
    def test_new_user_from_database(self, fake_fetch_user):
        fake_fetch_user.return_value = (1, None)

        self.app.new_user(1)

        self.assertIsNotNone(self.app.current_user)
        self.assertIsInstance(self.app.current_user, User)
        self.assertEqual(self.app.current_user.uid, 1)


if __name__ == '__main__':
    unittest.main()
