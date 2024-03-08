from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import json
import requests
import os
import sys
from PIL import Image
import torch

from osgeo import gdal

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
server_dir = os.path.join(parent_dir, 'server')
model_dir = os.path.join(parent_dir, 'model')


sys.path.append(parent_dir)
sys.path.append(server_dir)
sys.path.append(model_dir)

# print(f"paths to check for module: {sys.path}")

from server.settings import *
from model.models import SeResNext50_Unet_MultiScale
from model.data_preprocessing import tif_to_img

from .folium_maps import html_code
# from .plotly_maps import html_code
from .map_segmentation import html_code
# from .plotly_maps import dash_app

os.environ['TORCH_HOME'] = model_dir

def loginPage(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return render(request, "app/login.html")
        
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("LOGIN SUCCESSFUL, REDIRECTING TO HOME")
            return redirect('home')
        else: 
            messages.error(request, "Invalid credentials")
            return render(request, "app/login.html")
        
    return render(request, "app/login.html")



@login_required(login_url="login/")
def home(request):
    print(f"HII {request.user.username}, welcome to home page")
    api_url = "https://api.reliefweb.int/v1/reports?appname=apidoc&preset=latest&query[value]=earthquake&limit=6"
    api_response = requests.get(api_url)
    
    if api_response.status_code == 200:
        api_response_json = api_response.json()        
        reports = api_response_json.get("data", [])    
        # print(json.dumps(reports, indent=3))
        return render(request, 'app/home.html', {'reports': reports})
    else:
        messages.error(request, f"Failed to fetch data from API. Status code: {api_response.status_code}")
        return render(request, 'app/home.html')



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


def inferenceform(request):
    # if True:
    if request.method == 'POST' and request.FILES['pre_image'] and request.FILES['post_image']:

        pre_image = request.FILES['pre_image']
        post_image = request.FILES['post_image']
        city = request.POST['city']  
        date = request.POST['date']
        disaster_type = request.POST['disaster_type']

        pre_path = os.path.join(STATICFILES_DIRS[0], 'temp', 'pre.tif')
        post_path = os.path.join(STATICFILES_DIRS[0], 'temp', 'post.tif')
        with open(pre_path, 'wb') as f:
            for chunk in pre_image.chunks():
                f.write(chunk)
        with open(post_path, 'wb') as f:
            for chunk in post_image.chunks():
                f.write(chunk)

        pre_image = gdal.open(pre_path)
        post_image = gdal.open(post_path)
        
        pre, post = tif_to_img(pre_image), tif_to_img(post_image)        
        pre_post = torch.cat((pre, post), dim=-1).unsqueeze(0)

        model = SeResNext50_Unet_MultiScale()
        output = model(pre_post)

        print(f"\n\ninfereed successfully, output shape: {output.shape}")
        type(f"pre image type: {pre}")


        print(f"pre image: {type([pre]),pre.shape}")
        print(f"post image: {type([post]),post.shape}")
        print(f"output image: {type([output]),output.shape}")
    else:
        return render(request, "app/inferenceform.html")
        
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def notifications(request):
    pass