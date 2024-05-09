from django.test import TestCase, Client
from ..models import CustomUser, InferenceModel, LoginHistoryModel
from django.urls import reverse
from unittest.mock import patch
from django.contrib.messages import get_messages
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from random import choice
import json
from io import BytesIO
from datetime import datetime
from PIL import Image
from django.contrib import messages
from django.contrib.messages import get_messages
import os
from django.conf import settings
from ..inference.preprocessing import *








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
        print("TESTING SUCCESSFUL LOGIN----------------------------------------------")
        with patch('app.views.authenticate') as mock_authenticate:
            mock_authenticate.return_value = self.user
            # Simulate a POST request to loginPage with correct credentials
            response = self.client.post(reverse('login'), 
                                        {'username': self.user.username, 'password': self.user.password})
            # Check if the user is redirected to the home page
            self.assertRedirects(response, reverse('home'))
        print("LOGIN SUCCESSFUL------------------------------------------------\n\n")
            
    def test_login_wrong_username(self):
        print("TESTING WRONG USERNAME--------------------------------------------------")
        # Simulate a POST request to loginPage with incorrect credentials
        response = self.client.post(reverse('login'), {'username': 'invaliduser', "password": self.user.password})
        # print(response)
        # Check if the user stays on the login page and gets an error message
        self.assertRedirects(response, reverse('login'))
        messages = get_messages(response.wsgi_request)
        error_messages = [msg.message for msg in messages if msg.level == 40]  # 40 corresponds to the ERROR level
        self.assertIn("Invalid credentials", error_messages)
        print("WRONG USERNAME SUCESSFUL--------------------------------------------------\n\n")

    def test_login_wrong_password(self):
        print("TESTING WRONG PASSWORD-------------------------------------------------")
        # Simulate a POST request to loginPage with incorrect credentials
        response = self.client.post(reverse('login'), {'username': self.user.username, 'password': "invalidpassword"})
        # print(response)
        # Check if the user stays on the login page and gets an error message
        self.assertRedirects(response, reverse('login'))
        messages = get_messages(response.wsgi_request)
        error_messages = [msg.message for msg in messages if msg.level == 40]  # 40 corresponds to the ERROR level
        self.assertIn("Invalid credentials", error_messages)
        print("WRONG PASSWORD SUCESSFUL-------------------------------------------------\n\n")




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
        print("SUCCESS:LOGOUT----------")






class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='dell', password='dell')


    def test_home_view_with_authenticated_user(self):
        print("TESTING AUTHENTICATED HOME--------------------------------------------------")
        # login
        self.client.login(username='dell', password='dell')
        # go to home page
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        print("SUCCESS: AUTHENTICATED HOME--------------------------------------------------\n\n")


    def test_home_view_with_unauthenticated_user(self):
        print("TESTING UNAUTHENTICATED HOME------------------------------------------------------")
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=%2F', status_code=302)
        print("SUCCESS: UNAUTHENTICATED HOME------------------------------------------------------\n\n")



class AdminPanelTestCase(TestCase):
    # create test user 
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='password123', is_admin=True
        )
        self.client.force_login(self.user)
        print("\n\n")

    def test_admin_panel_view(self):
        print("Checking admin panel view----------------------")
        # Check if the user is logged in
        self.assertTrue(self.user.is_authenticated)

        # Try accessing the admin panel
        response = self.client.get(reverse('admin-panel'))

        # Check the response status code and template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/adminPanel.html')
        print("success----------------------------------------\n\n")


    def test_get_user_details(self):
        print("checking get_user_details-------------------")
        # Get all user ids from the database
        user_ids = CustomUser.objects.values_list('id', flat=True)
        # Choose a random user id
        random_user_id = choice(user_ids)
        # Fetch details of the random user
        response = self.client.get(reverse('get-user-details', kwargs={'user_id': random_user_id}))
        self.assertEqual(response.status_code, 200)
        print("success--------------------------------\n\n")


    def test_add_user_view(self):
        print("checking add user---------------------------")
        response = self.client.post(reverse('add-user'), data={
            'username': 'newuser', 'email': 'newuser@example.com',
            'contact': '1234567890', 'password': 'newpassword123',
            'firstName': 'New', 'lastName': 'User', 'is_admin': 'True'
        })
        self.assertEqual(response.status_code, 302) 
        print("success--------------------------------\n\n")


    def test_edit_user_view(self):
        print("checking edit user---------------------------")
        # get random user to edit 
        user_ids = CustomUser.objects.values_list('id', flat=True)
        random_user_id = choice(user_ids)
        response = self.client.get(reverse('get-user-details', kwargs={'user_id': random_user_id}))
        content = json.loads(response.content)
        switch = False if content["is_admin"]==True else True
        # switch roles
        response = self.client.post(reverse('edit-user', kwargs={'user_id': random_user_id}), data={'is_admin': switch})
        
        self.assertEqual(response.status_code, 302)  
        # Refresh the user instance from the database to check if the role has been switched
        updated_employee_user = CustomUser.objects.get(id=random_user_id)
        self.assertEqual(updated_employee_user.is_admin, switch) 
        print("success--------------------------------\n\n")

    
    def test_delete_user_view(self):
        print("checking delete user---------------------------")
        # Get all user ids from the database
        user_ids = CustomUser.objects.values_list('id', flat=True)
        # Choose a random user id
        random_user_id = choice(user_ids)
        response = self.client.post(reverse('delete-user', kwargs={'user_id': random_user_id}))
        self.assertEqual(response.status_code, 302)  # Redirects after successful user deletion
        self.assertFalse(CustomUser.objects.filter(id=random_user_id).exists())
        print("success--------------------------------\n\n")


class ProfileViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='password123',
            first_name='Test', last_name='User', contact='1234567890', location='Test Location'
        )
        self.client = Client()
        self.client.force_login(self.user)
        print("\n\n")

    def test_profile_view_authenticated(self):
        # changing the profile content 
        print("Viewing profile user---------------------------")
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        print("success----------------------------------------")

    def test_profile_view_post(self):
        # Make a POST request to the profile view
        print("Chnaging the profile content---------------------------")
        response = self.client.post(reverse('profile'), data={
            'first_name': 'Updated First Name',
            'last_name': 'Updated Last Name',
            'email': 'updated@example.com',
            'contact-number': '9876543210',
            'location': 'Updated Location',
        })
        # Check the response status code and redirection
        self.assertRedirects(response, reverse('profile'))

        # Check if profile was updated
        updated_user = CustomUser.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'Updated First Name')
        self.assertEqual(updated_user.last_name, 'Updated Last Name')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.contact, '9876543210')
        self.assertEqual(updated_user.location, 'Updated Location')
        print("success----------------------------------------")



class InferenceDashboardMapViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='password123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        print("\n\n")


    def create_dummy_tiff(self, width, height):
        # Create a blank TIFF image using PIL
        image = Image.new('RGB', (width, height))
        with BytesIO() as buffer:
            image.save(buffer, format='TIFF')
            return buffer.getvalue()


    def test_empty_tiff_files(self):
        # Create temporary TIFF files for testing
        pre_tiff_data = self.create_dummy_tiff(1024, 1024)
        post_tiff_data = self.create_dummy_tiff(1024, 1024)

        pre_tiff_io = BytesIO(pre_tiff_data)
        post_tiff_io = BytesIO(post_tiff_data)
        print(type(pre_tiff_data))

        pre_tiff_io.name = 'pre_image.tif'
        post_tiff_io.name = 'post_image.tif'    

        # Prepare form data
        form_data = {
            'city': 'Test City',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'disaster_type': 'Test Disaster Type',
            'disaster_description': 'Test Disaster Description',
            'comments': 'Test Comments',
            'pre_image': pre_tiff_io,
            'post_image': post_tiff_io,
        }
        # Make a POST request to the inferenceform view with form data and ampty tiff files, 
        response = self.client.post(reverse('inferenceform'), data=form_data, follow=False)
        storage = messages.get_messages(response.wsgi_request)
        messages_list = [msg.message for msg in storage]
        self.assertIn('Uploaded TIFF files do not contain geospatial information.', messages_list)
        self.assertRedirects(response, reverse('inferenceform'))


    def test_select_tiff_files(self):
        # Get the path to the directory containing sample TIFF files
        sample_tiff_dir = os.path.join(settings.BASE_DIR, "app", "test_batches")

        # Get a list of sample TIFF files in the directory
        sample_tiff_files = [file for file in os.listdir(sample_tiff_dir) if file.endswith('.tif') and "pre" in file]
        for index, file_name in enumerate(sample_tiff_files):
            print(f"{index+1}: {file_name}")
        pre = sample_tiff_files[int(input("Please tell which disaster you want to test: "))-1]
        post = pre.replace("pre", "post")

        with open(os.path.join(sample_tiff_dir, pre), 'rb') as pre_file, open(os.path.join(sample_tiff_dir, post), 'rb') as post_file:
            pre_tiff_io = BytesIO(pre_file.read())
            post_tiff_io = BytesIO(post_file.read())
        
        form_data = {
            'pre_image': pre_tiff_io,
            'post_image': post_tiff_io,
            'city': 'Test City',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'disaster_type': 'Test Disaster Type',
            'disaster_description': 'Test Disaster Description',
            'comments': 'Test Comments',
        }
    
        response = self.client.post(reverse('inferenceform'), data=form_data, follow=True)
        messages_list = [msg.message for msg in messages.get_messages(response.wsgi_request)]
        self.assertIn('InferenceModel model created', messages_list)

        inference_model = InferenceModel.objects.filter(user=self.user).last()
        self.assertIsNotNone(inference_model)  # Ensure the InferenceModel instance exists

        # Make a GET request to the map view with the inference model ID
        map_response = self.client.get(reverse('map_with_id', kwargs={'inference_id': inference_model.id}))
        self.assertEqual(map_response.status_code, 200)
        self.assertTemplateUsed(map_response, 'app/map.html')
        self.assertIn('context', map_response.context)
