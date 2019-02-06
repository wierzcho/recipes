from unittest.mock import patch

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

    def test_get_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_get_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Juicy burger",
            time_minutes=5,
            price=20.5,
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'img.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)
