from django.test import TestCase, Client
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


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from django.contrib.messages.storage.fallback import FallbackStorage

class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='dell', password='dell')

    def test_home_view_with_authenticated_user(self):
        self.client.login(username='dell', password='dell')
        response = self.client.get(reverse('home'))
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertIn(b'HII dell, welcome to home page', response.content)

    def test_home_view_with_unauthenticated_user(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=/home/', status_code=302)

    @patch('app.views.get_news')
    def test_home_view_with_api_data(self, mock_get_news):
        mock_get_news.return_value = [{'title': 'Test Report 1'}, {'title': 'Test Report 2'}]
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertIn(b'Test Report 1', response.content)
        self.assertIn(b'Test Report 2', response.content)

    @patch('app.views.requests.get')
    def test_home_view_with_api_failure(self, mock_requests_get):
        mock_requests_get.return_value.status_code = 500
        storage = FallbackStorage(self.client.session)
        self.client._messages = storage
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertIn(b'Failed to fetch data from API', response.content)
