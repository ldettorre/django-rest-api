from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''test the users api (public)'''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''test creating user with valid payload is successful'''
        payload = {
            'email': 'test@gmail.com',
            'password': 'test123',
            'name': 'Peter Parker'
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        '''test creating a user that already exists fails'''
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'Peter Parker'
            }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''test that the password must be more than 5 characters'''
        payload = {'email': 'test@gmail.com', 'password': 'pw'}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''test that a token is created for the user'''
        payload = {'email': 'test@gmail.com', 'password': 'test123'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        '''test that token is not created if invalid credentials are given'''
        create_user(email='test@gmail.com', password='test123')
        payload = {'email': 'test@gmail.com', 'password': 'wrong'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''test that the token is not created if user doesn't exist'''
        payload = {'email': 'test@gmai.com', 'password': 'test123'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        '''test that email and password are required'''
        response = self.client.post(TOKEN_URL,
                                    {'email': 'one', 'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        '''test that authentication is required for users'''
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    '''test api requests that require authentication'''
    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpassword',
            name='name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        '''test retrieving profile for logged in used'''
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

        def test_post_me_not_allowed(Self):
            '''test that posts is not allowed on the me url'''
            response = self.client.post(ME_URL, {})

            self.assertEqual(response.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_profile(self):
            '''test updating the user profile for authenticated users'''
            payload = {'name': 'new name', 'password': 'newpassword123'}

            response = self.client.patch(ME_URL, payload)

            self.user.refresh_from_db()
            self.assertEqual(self.user.name, payload('name'))
            self.assertTrue(self.user.check_password(payload['password']))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
