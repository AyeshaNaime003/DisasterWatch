from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import requests
import os
from osgeo import gdal

# Import sys module to manipulate Python path
import sys
import os

# Add the parent directory of 'server' and 'app' to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
server_dir = os.path.join(parent_dir, 'server')
sys.path.append(parent_dir)
sys.path.append(server_dir)

# Now you can import variables from settings.py
from server.settings import *

from .folium_maps import html_code
# from .plotly_maps import html_code
from .map_segmentation import html_code
# from .plotly_maps import dash_app

def loginPage(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "No user with this username")
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("LOGIN SUCCESSFUL, REDIRECTING TO HOME")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "app/login.html")

# Create your views here.
@login_required(login_url="login/")
def home(request):
    print(f"HII {request.user.username}, welcome to home page")
    api_url = "https://api.reliefweb.int/v1/reports?appname=apidoc&preset=latest&query[value]=earthquake&limit=6"
    response = requests.get(api_url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        api_data = response.json()        
        reports = api_data.get("data", [])    
        # for key
        return render(request, 'app/home.html', {'reports': reports})
    else:
        # Handle the error gracefully
        error_message = f"Failed to fetch data from API. Status code: {response.status_code}"
        return render(request, 'app/home.html', {'error_message': error_message})



def about(request):
    return render(request, "app/about.html")

@login_required(login_url="login/")
def logoutPage(request):
    logout(request)
    return redirect("login")

def map(request):
    return render(request, 'app/map.html', context={'html_code': html_code,})

def adminPanel(request):
     return render(request, "app/adminPanel.html")

def dashboard(request):
    return render(request, "app/dashboard.html")

def profile(request):
    user = request.user
    if request.method == 'POST':
         # Get the data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Update user attributes
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        
        # Save the changes
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    else:
        return render(request, "app/profile.html", context={'user': user,})

def help(request):
    return render(request, "app/help.html")

def notifications(request):
    return render(request, "app/notifications.html")

def inferenceform(request):
    if request.method == 'POST' and request.FILES['imageFile']:
        print()
        image_file = request.FILES['imageFile']
        city = request.POST['city']
        date = request.POST['date']

        
        file_path = os.path.join(STATICFILES_DIRS[0], 'temp', 'temp.tif')
        with open(file_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Open the TIFF file and read its metadata
        dataset = gdal.Open(file_path)
        metadata = dataset.GetMetadata()

        # Close the dataset
        dataset = None

        # Delete the temporary file
        os.remove(file_path)

        # Display the city, date, and metadata
        print("City:", city)
        print("Date:", date)
        print("Metadata:")
        for key, value in metadata.items():
            print(f"{key}: {value}")

        return HttpResponse("Processing completed. Check the server console for details.")
    else:
        return render(request, "app/inferenceform.html")
        