import json
import time
import unittest

import requests

mock_user_ok = {
    "user_id": 12345,
    "user_name": "TestUserOk"
}

mock_user_ko = {
    "user_name": "TestUserKo"
}


class TestApiDemoUsers(unittest.TestCase):

    def setUp(self) -> None:
        self.__api_url = "http://localhost:8080/users"
        self.__api_user = f"{self.__api_url}/{mock_user_ok['user_id']}"
        self.__api_user_init = f"{self.__api_url}/init"
        self.__headers = {
            "Content-Type": "application/json"
        }

    def test_health(self):
        url = f"{self.__api_url}/health"
        response = requests.get(url, headers=self.__headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"message": "Ok"})

    def test_init(self):
        url = f"{self.__api_url}/init"
        response = requests.get(url, headers=self.__headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"message": "Database ready"})

    def test_get_user(self):
        requests.get(self.__api_user_init, headers=self.__headers)
        requests.post(self.__api_url, data=json.dumps(mock_user_ok), headers=self.__headers)
        response = requests.get(self.__api_user, headers=self.__headers)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), mock_user_ok)

        requests.delete(self.__api_user, headers=self.__headers)
        response = requests.get(self.__api_user, headers=self.__headers)
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {"message": "NotFound"})

    def test_delete_user(self):
        requests.get(self.__api_user_init, headers=self.__headers)
        requests.post(self.__api_url, data=json.dumps(mock_user_ok), headers=self.__headers)
        response = requests.delete(self.__api_user, headers=self.__headers)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, "")

        response = requests.delete(self.__api_user, headers=self.__headers)
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {"message": "NotFound"})

    def test_create_user(self):
        requests.get(self.__api_user_init, headers=self.__headers)
        response = requests.post(self.__api_url, data=json.dumps(mock_user_ok), headers=self.__headers)
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), {"message": "Created"})

        response = requests.post(self.__api_url, data=json.dumps(mock_user_ko), headers=self.__headers)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {"message": "BadRequest"})
