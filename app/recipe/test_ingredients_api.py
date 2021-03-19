from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    '''test publicly available ingredients API'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''test that login is required to access endpoint'''
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    '''test private ingredients API'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com'
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        '''test retrieve a list of ingredients'''
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        response = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        '''test that ingredients for the authenticated user are returned'''
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass1'
        )
        Ingredient.objects.create(user=user2, name='Pasta')

        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        '''test create new ingredient'''
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''test creating invalid ingredient fails'''
        payload = {'name': ''}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
