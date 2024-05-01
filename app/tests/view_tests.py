from django.test import TestCase, Client
from ..models import CustomUser, InferenceModel, LoginHistoryModel
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


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


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='dell', password='dell')

    def test_home_view_with_authenticated_user(self):
        print("TESTING AUTHENTICATED HOME------------------------------------------------------")
        # login
        self.client.login(username='dell', password='dell')
        # go to home page
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        print("SUCCESS: AUTHENTICATED HOME------------------------------------------------------\n\n")


    def test_home_view_with_unauthenticated_user(self):
        print("TESTING UNAUTHENTICATED HOME------------------------------------------------------")
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=%2F', status_code=302)
        print("SUCCESS: UNAUTHENTICATED HOME------------------------------------------------------\n\n")

class LogoutPageTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='test', email='test@example.com', password='test')
        self.client = Client()
        self.client.login(username=self.user.username, password=self.user.password)
        LoginHistoryModel.objects.create(user=self.user, login_time=timezone.now())

    def test_logout_page(self):
        print("TESTING LOGOUT----------")
        self.assertTrue(self.user.is_authenticated)
        response = self.client.get(reverse('logout'))
        self.client.session.flush()
        self.assertEqual(response.status_code, 302)
        print("SUCCESS:  LOGOUT----------")
11

class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='admin', email='admin@example.com', password='admin')
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def test_admin_panel_page(self):
        response = self.client.get(reverse('admin-panel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/adminPanel.html')

    def test_add_user(self):
        initial_users_count = CustomUser.objects.count()
        response = self.client.post(reverse('add-user'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'contact': '1234567890',
            'password': 'testpass',
            'firstName': 'Test',
            'lastName': 'User',
            'is_admin': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful addition
        self.assertEqual(CustomUser.objects.count(), initial_users_count + 1)  # User added

    def test_edit_user(self):
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        user_id = user.id
        response = self.client.post(reverse('edit-user', kwargs={'user_id': user_id}), {'is_admin': 'on'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        edited_user = CustomUser.objects.get(id=user_id)
        self.assertTrue(edited_user.is_admin)  # User's admin status updated

    def test_delete_user(self):
        user = CustomUser.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        user_id = user.id
        initial_users_count = CustomUser.objects.count()
        response = self.client.post(reverse('delete-user', kwargs={'user_id': user_id}))
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertEqual(CustomUser.objects.count(), initial_users_count - 1)  # User deleted