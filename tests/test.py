import os
import unittest
from unittest.mock import MagicMock, patch
from src import ChiaNFTHelper
import requests

class TestChiaNFTHelper(unittest.TestCase):

    def setUp(self):
        self.collection_id = "test_collection"
        self.require_owners = True
        self.output_file = "output.xlsx"
        self.unique = False

    def test_fetch_data(self):
        helper = ChiaNFTHelper(self.collection_id, self.require_owners)
        helper.url = "https://api.mintgarden.io/collections/col1wt3rv8fqmw5ydmlg6fqdpxfrag9rn8taz7uk38daawu7gfzlecrsp049hu/nfts"
        helper.fetch_data()
        self.assertIsNotNone(helper.data)
        self.assertIn("items", helper.data)

    @patch("requests.get")
    def test_fetch_data_with_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Error")
        helper = ChiaNFTHelper(self.collection_id, self.require_owners)
        helper.url = "https://api.mintgarden.io/collections/col1wt3rv8fqmw5ydmlg6fqdpxfrag9rn8taz7uk38daawu7gfzlecrsp049hu/nfts"
        helper.fetch_data()
        self.assertIsNone(helper.data)

    def test_addresses_ids(self):
        helper = ChiaNFTHelper(self.collection_id, self.require_owners)
        helper.data = {
            "items": [
                {"encoded_id": "1", "owner_address_encoded_id": "A", "owner_encoded_id": "DID1"},
                {"encoded_id": "2", "owner_address_encoded_id": "B", "owner_encoded_id": "DID2"},
                {"owner_address_encoded_id": "C"},
                {"encoded_id": "4", "owner_encoded_id": None}
            ]
        }
        helper.addresses_ids()
        self.assertIn("owner_ids", helper.data)
        self.assertEqual(len(helper.data["owner_ids"]), 4)
        self.assertEqual(helper.data["owner_ids"][0]["encoded_id"], "1")
        self.assertEqual(helper.data["owner_ids"][0]["owner_address_encoded_id"], "A")
        self.assertEqual(helper.data["owner_ids"][0]["owner_encoded_id"], "DID1")
        self.assertEqual(helper.data["owner_ids"][2]["owner_address_encoded_id"], "C")
        self.assertEqual(helper.data["owner_ids"][2]["owner_encoded_id"], "No DID")

    def test_print_results(self):
        helper = ChiaNFTHelper(self.collection_id, self.require_owners)
        helper.data = {
            "owner_ids": [
                {"encoded_id": "1", "owner_address_encoded_id": "A", "owner_encoded_id": "DID1"},
                {"encoded_id": "2", "owner_address_encoded_id": "B", "owner_encoded_id": "DID2"},
                {"encoded_id": "3", "owner_address_encoded_id": "C", "owner_encoded_id": "DID1"}
            ]
        }
        helper.print_results(self.output_file, self.unique)
        self.assertTrue(os.path.exists(self.output_file))
        os.remove(self.output_file)

    def test_run(self):
        helper = ChiaNFTHelper(self.collection_id, self.require_owners)
        helper.fetch_data = MagicMock()
        helper.addresses_ids = MagicMock()
        helper.print_results = MagicMock()
        helper.run(self.output_file, self.unique)
        helper.fetch_data.assert_called_once()
        helper.addresses_ids.assert_called_once()
        helper.print_results.assert_called_once_with(self.output_file, self.unique)

if __name__ == "__main__":
    unittest.main()
