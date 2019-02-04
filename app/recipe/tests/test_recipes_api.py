from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **kwargs):
    defaults = {
        'title': 'title',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(kwargs)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipesApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.pl",
            password="passwirdasdasd",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
