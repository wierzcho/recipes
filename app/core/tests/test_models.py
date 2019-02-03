from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@test.pl", password="passpass123"):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = "test@test.pl"
        password = "testtest123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_check_if_user_email_domain_is_lowercased(self):
        email = "test@TEST.pl"
        password = "testtest1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                password="test1234",
            )

    def test_new_user_is_superuser(self):
        user = get_user_model().objects.create_superuser(
            email="email@test.pl",
            password="password",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_get_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="vegan"
        )

        self.assertEqual(str(tag), tag.name)
