"""
LESSON 2.1: EX. 1
"""
import sys
sys.path.extend(['C:\\Users\\Jediroman\\Desktop\\PyCharmProjects\\netology_lessons',
                 'C:/Users/Jediroman/Desktop/PyCharmProjects/netology_lessons'])
import unittest
import json
from unittest.mock import patch
import advanced.solution2_1.doc_manager as doc_mngr

documents = []
directories = {}


@patch('advanced.solution2_1.doc_manager.documents', documents)
@patch('advanced.solution2_1.doc_manager.directories', directories)
class TestSecretary(unittest.TestCase):

    test_shelf = "4"
    test_doc = {
        "type": 'passport',
        "number": '1234 567890',
        "name": 'Вася Петечкин'}

    def setUp(self):
        with open('fixtures/documents.json', 'r', encoding='utf-8') as out_docs:
            documents.extend(json.load(out_docs))
        with open('fixtures/directories.json', 'r', encoding='utf-8') as out_dirs:
            directories.update(json.load(out_dirs))

    def tearDown(self):
        documents.clear()
        directories.clear()

    def test_add_new_doc(self):
        fake_input = [self.test_doc['number'],
                      self.test_doc['type'],
                      self.test_doc['name'],
                      self.test_shelf]

        with patch('builtins.input', side_effect=fake_input):
            added_shelf = doc_mngr.add_new_doc()

        self.assertEqual(added_shelf, self.test_shelf, 'Shelf addition failed')
        self.assertIn(self.test_doc, documents, 'Document addition failed')

    def test_append_doc_to_shelf(self):
        doc_mngr.append_doc_to_shelf(self.test_doc['number'], self.test_shelf)

        self.assertIn(self.test_shelf, directories, "Shelf addition failed")
        self.assertIn(self.test_doc['number'], directories[self.test_shelf], "Document addition failed")

    def test_add_new_shelf(self):
        doc_mngr.add_new_shelf(self.test_shelf)

        self.assertIn(self.test_shelf, directories, 'Shelf addition failed')

    def test_check_doc_exists(self):
        self.assertTrue(doc_mngr.check_document_existance('2207 876234'), "Existance check failed")
        self.assertFalse(doc_mngr.check_document_existance('this document doesnt exist'), "Non-existance cheeck failed")

    def test_delete_doc(self):
        with patch('builtins.input', return_value='2207 876234'):
            deleted_doc, result = doc_mngr.delete_doc()

        self.assertTrue(result, 'Document deletion failed')
        self.assertEqual(deleted_doc, '2207 876234', 'Wrong document deleted')

    def test_get_owner_info(self):
        with patch('builtins.input', return_value='2207 876234'):
            owner = doc_mngr.get_doc_owner_name()

        self.assertEqual(owner, documents[0]['name'], "Getting owner name failed")

        with patch('builtins.input', return_value='fake!'):
            owner = doc_mngr.get_doc_owner_name()

        self.assertIsNone(owner, "Getting fake owner name succesfully")

    @patch('builtins.print')
    def test_move_doc(self, _):
        with patch('builtins.input', side_effect=['11-2', '2']):
            doc_mngr.move_doc_to_shelf()

        self.assertNotIn('11-2', directories['1'], "Document removal failed")
        self.assertIn('11-2', directories['2'], "Document appendage failed")


if __name__ == '__main__':
    unittest.main(verbosity=2)
