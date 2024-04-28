from django.test import TestCase
from ..models import CustomUser, InferenceModel, LoginHistoryModel
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages

# Create your tests here.
class LoginTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='dell',
            password='dell'
        )
    def test_login_successful(self):
        # Mock the authenticate function to return the test user
        print("TESTING SUCCESSFUL LOGIN------------------------------------------------------")
        with patch('app.views.authenticate') as mock_authenticate:
            mock_authenticate.return_value = self.user
            # Simulate a POST request to loginPage with correct credentials
            response = self.client.post(reverse('login'), 
                                        {'username': self.user.username, 'password': self.user.password})
            # Check if the user is redirected to the home page
            self.assertRedirects(response, reverse('home'))
        print("LOGIN SUCCESSFUL------------------------------------------------------\n\n")
            

    def test_login_wrong_username(self):
        print("TESTING WRONG USERNAME------------------------------------------------------")
        # Simulate a POST request to loginPage with incorrect credentials
        response = self.client.post(reverse('login'), {'username': 'invaliduser', "password": self.user.password})
        # print(response)
        # Check if the user stays on the login page and gets an error message
        self.assertRedirects(response, reverse('login'))
        messages = get_messages(response.wsgi_request)
        error_messages = [msg.message for msg in messages if msg.level == 40]  # 40 corresponds to the ERROR level
        self.assertIn("Invalid credentials", error_messages)
        print("WRONG USERNAME SUCESSFUL------------------------------------------------------\n\n")

    def test_login_wrong_password(self):
        print("TESTING WRONG PASSWORD------------------------------------------------------")
        # Simulate a POST request to loginPage with incorrect credentials
        response = self.client.post(reverse('login'), {'username': self.user.username, 'password': "invalidpassword"})
        # print(response)
        # Check if the user stays on the login page and gets an error message
        self.assertRedirects(response, reverse('login'))
        messages = get_messages(response.wsgi_request)
        error_messages = [msg.message for msg in messages if msg.level == 40]  # 40 corresponds to the ERROR level
        self.assertIn("Invalid credentials", error_messages)
        print("WRONG PASSWORD SUCESSFUL------------------------------------------------------\n\n")
