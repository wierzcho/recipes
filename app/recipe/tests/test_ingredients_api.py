from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicRecipesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.pl",
            password="pass1234"
        )

    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesAPiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="adasd@ad.pl",
            password="test1234"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        Ingredient.objects.create(name="ingredient1", user=self.user)
        Ingredient.objects.create(name="ingredient2", user=self.user)
        all_ingredients = Ingredient.objects.all()

        ingredients_serialized = IngredientSerializer(all_ingredients,
                                                      many=True, )
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients_serialized.data, res.data)

    def test_retrieve_only_user_created_ingredients(self):
        user2 = get_user_model().objects.create_user(
            email="adasdasdasdasd@asdasdasd.pl",
            password="halohalohalhaohlaho",
        )
        mine_ingredient1 = Ingredient.objects.create(name="ingredient1",
                                                     user=self.user)
        mine_ingredient2 = Ingredient.objects.create(name="ingredient2",
                                                     user=self.user)
        not_mine_ingredient = Ingredient.objects.create(name="ingredient3",
                                                        user=user2)

        logged_in_users_ingredients = Ingredient.objects.filter(
            user=self.user,
        ).order_by('-name')

        should_not_exist = logged_in_users_ingredients \
            .filter(user=user2) \
            .exists()

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(should_not_exist)
        self.assertEqual(res.data[0]['name'], mine_ingredient1.name)

    def test_add_ingredient_successful(self):
        payload = {"name": "test1234", }

        res = self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(name=payload['name']).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_add_ingredient_not_successful(self):
        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
