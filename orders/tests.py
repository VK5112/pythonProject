from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='string', email='user@example.com', password='password123')

    def test_login_with_email(self):
        url = reverse('token_obtain_pair')
        data = {'email': 'testuser@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserListTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        self.client.login(username='admin', password='admin123')

    def test_get_users(self):
        url = reverse('admin_users_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
