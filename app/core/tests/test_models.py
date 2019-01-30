from django.test import TestCase
from django.contrib.auth import get_user_model


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
