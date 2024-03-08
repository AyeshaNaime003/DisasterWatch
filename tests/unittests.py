from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch


# class LoginTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.username = 'dell'
#         self.password = 'dell'
#         self.user = User.objects.create_user(username=self.username, password=self.password)
    
#     def test_login_correct_credentials(self):
#         response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
#         self.assertEqual(response.status_code, 302)  
    
    
#     def test_wrong_username(self):
#         response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': self.password})
#         self.assertEqual(response.status_code, 200)


#     def test_wrong_password(self):
#         response = self.client.post(reverse('login'), {'username': self.username, 'password': 'wrongpassword'})
#         self.assertEqual(response.status_code, 200)
       

#     def test_logout(self):
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('logout'))
#         self.assertEqual(response.status_code, 302)

# class OtherPagesTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.username = 'dell'
#         self.password = 'dell'

#     def test_home(self):
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('home'))
#         self.assertEqual(response.status_code, 200)
    
#     def test_profile(self):
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('profile'))
#         self.assertEqual(response.status_code, 200)
    
#     def test_help(self):
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('help'))
#         self.assertEqual(response.status_code, 200)
    
#     def test_inferenceform(self):
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('inferenceform'))
#         self.assertEqual(response.status_code, 200)


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('app.views.requests.get')
    def test_home_successful_api_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "reports": []
        }
        response = self.client.get(reverse('home'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reports' in response)
        # self.assertEqual(len(response.context['reports']), 3)

    # @patch('app.views.requests.get')
    # def test_home_failed_api_response(self, mock_get):
    #     mock_get.return_value.status_code = 404
    #     response = self.client.get(reverse('home'))
    #     self.assertEqual(response.status_code, 200)
    #     messages = [str(message) for message in get_messages(response)]
    #     self.assertIn('Failed to fetch data from API. Status code: 404', messages)

    # @patch('app.views.requests.get')
    # def test_home_render_template_with_data(self, mock_get):
    #     mock_get.return_value.status_code = 200
    #     mock_get.return_value.json.return_value = {
    #         "data": ["report1", "report2", "report3"]
    #     }
    #     response = self.client.get(reverse('home'))
    #     self.assertTemplateUsed(response, 'app/home.html')
    #     self.assertTrue('reports' in response.context)
    #     self.assertEqual(len(response.context['reports']), 3)

    # @patch('app.views.requests.get')
    # def test_home_render_template_without_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertTrue('reports' in response.context)
        self.assertEqual(len(response.context['reports']), 0)