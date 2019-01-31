from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_created_successfully(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'password',
            'name': 'name',
        }

        res = self.client.post(CREATE_USER_URL, credentials)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password((credentials['password'])))
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'password',
            'name': 'name',
        }

        create_user(**credentials)
        res = self.client.post(CREATE_USER_URL, credentials)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'pw',
            'name': 'name',
        }
        res = self.client.post(CREATE_USER_URL, credentials)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects \
            .filter(email=credentials['email']) \
            .exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'password',
        }
        create_user(**credentials)
        res = self.client.post(TOKEN_URL, credentials)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'wrong',
        }

        res = self.client.post(TOKEN_URL, credentials)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        credentials = {
            'email': 'test@test.pl',
            'password': 'passas',
        }

        res = self.client.post(TOKEN_URL, credentials)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        res = self.client.post(
            TOKEN_URL, {"email": "asd@asd.pl", "password": ""}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
