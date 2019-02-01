from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
USER_URL = reverse("user:main")


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

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.pl",
            password="password",
            name="name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successfull(self):
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_not_allowed(self):
        res = self.client.post(USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile_update_page(self):
        payload = {
            "password": "passdsad",
            "name": "name"
        }

        res = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
