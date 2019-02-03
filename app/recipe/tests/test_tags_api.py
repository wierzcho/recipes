from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class PublicTagAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.pl",
            password="passpasspass",
            name="name",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="vegan")
        Tag.objects.create(user=self.user, name="cookie")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_tags_for_current_logged_in_user(self):
        user2 = get_user_model().objects.create_user(
            email="bla@bla.com",
            password="helloasd123",
            name="asdasd",
        )

        Tag.objects.create(user=user2, name="fruit")
        Tag.objects.create(user=self.user, name="vegetable")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
