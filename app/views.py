from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import CustomUser, JsonFileModel
import json
import requests
import os
import sys
from PIL import Image
import torch
from osgeo import gdal
import cv2
import json
import matplotlib.pyplot as plt
from datetime import datetime

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
from model.data_preprocessing import tif_to_img, one_hot_encoding_mask, mask_to_polygons, polygons_to_masks, get_tif_transform, pixels_to_coordinates
# from .get_lat_long import get_important_coordinates

# from .folium_maps import html_code
# # from .plotly_maps import html_code
# from .map_segmentation import html_code
# from .plotly_maps import dash_app

os.environ['TORCH_HOME'] = model_dir

def loginPage(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return redirect("login")
        
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("LOGIN SUCCESSFUL, REDIRECTING TO HOME")
            return redirect('home')
        else: 
            messages.error(request, "Invalid credentials")
            return redirect("login")
    else:
        messages.error(request, None)
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


@login_required(login_url="login/")
def about(request):
    return render(request, "app/about.html")


@login_required(login_url="login/")
def logoutPage(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login/")
def map(request): 
    # get data from database
    json_data = json.loads(JsonFileModel.objects.filter(user=request.user).last().json_file)
    date = json_data.get("date")   
    city = json_data["city"]   
    disaster_type = json_data["disaster_type"]   
    disaster_description = json_data["disaster_description"]   
    comments = json_data["comments"]   
    pre_path = json_data["pre_path"]   
    post_path = json_data["post_path"]   
    polygon_data = json_data["polygon_data"]   
        
    transform = get_tif_transform(pre_path)
    middle_lat, middle_long = pixels_to_coordinates(transform, (612,612))
    context = {
        'date': date,
        'city': city,
        'disaster_type': disaster_type,
        'disaster_description': disaster_description,
        'comments': comments,
        'pre_path': pre_path,
        'post_path': post_path,
        'polygon_data': polygon_data,
        'important_coordinates': {
            'middle_lat': middle_lat,
            'middle_long': middle_long,
        }
    }
    return render(request, 'app/map.html', context={'context': context})


@login_required(login_url="login/")
def adminPanel(request):
     return render(request, "app/adminPanel.html")


@login_required(login_url="login/")
def dashboard(request):
    return render(request, "app/dashboard.html")


@login_required(login_url="login/")
def profile(request):
    user = request.user
    print(user.email, user.first_name, user.last_name, user.contact, user.profile_picture.url)
    if request.method == 'POST':
         # Get the data from the form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact-number')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')
        

        # Update user attributes
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.contact = contact_number
        user.bio = bio
        if profile_picture:
            user.profile_picture.delete()
            user.profile_picture = profile_picture
            print("picture saved")
        # Save the changes
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    else:
        return render(request, "app/profile.html", context={'user': user,})


@login_required(login_url="login/")
def help(request):
    return render(request, "app/help.html")


@login_required(login_url="login/")
def inferenceform(request):
    # if True:
    if request.method == 'POST' and request.FILES['pre_image'] and request.FILES['post_image']:
        # get data from form
        pre_image = request.FILES['pre_image']
        post_image = request.FILES['post_image']
        city = request.POST['city']  
        date = request.POST['date']
        disaster_type = request.POST['disaster_type']
        disaster_description = request.POST['disaster_description']
        comments = request.POST['comments']

        # save the tiff files temporarily in media root
        file_name = f"{date}_{city}_{disaster_type}"
        pre_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_pre.tif")
        post_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_post.tif")
        with open(pre_path, 'wb') as f: 
            for chunk in pre_image.chunks():
                f.write(chunk)
        with open(post_path, 'wb') as f:
            for chunk in post_image.chunks():
                f.write(chunk)
        print("pre and post tifs saved")
        
        # convert the tiff files to RGB images to run for inference
        pre_tif, post_tif = gdal.Open(pre_path), gdal.Open(post_path)
        pre_image, post_image = torch.from_numpy(tif_to_img(pre_tif)), torch.from_numpy(tif_to_img(post_tif))
        pre_post = torch.cat((pre_image, post_image), dim=2).permute(2,0,1).unsqueeze(0).to(torch.float)
        print(f"Tifs converted to concatenated images of {pre_post.shape}, {pre_post.dtype}")
        # INFERENCE------------------------------------------------------------------
        # model = SeResNext50_Unet_MultiScale()
        # output = model(pre_post)
       
        # DUMMY DATA----------------------------------------------------------------------
        dummy_mask = cv2.imread("woolsey-fire_00000715_post_disaster.png") 
        print(f"Dummy mask shape an type {dummy_mask.shape}, {dummy_mask.dtype}")
        dummy_masks = one_hot_encoding_mask(dummy_mask)
        print(f"Dummy mask after hot encoding  {dummy_masks.shape}, {dummy_masks.dtype}")
        tranform = get_tif_transform(pre_path)
        classes=["red","orange","yellow","green"]
        # format the inference for database
        polygons_data={}
        for i, mask in enumerate(dummy_masks):
            color=classes[i]
            _, mask = cv2.threshold(mask.astype('uint8'), 0, 255, cv2.THRESH_BINARY)
            # print(f"{color} mask {mask.shape} {mask.dtype} {mask.max()}")
            polygons_in_mask = mask_to_polygons(mask, tranform, rdp=False)
            # print(polygons_in_mask[:5])
            print(f"{color}: {len(polygons_in_mask)}")
            polygons_data[color]=polygons_in_mask
        # Convert the dictionary to JSON format
        json_data = json.dumps({
            "date": date,
            "city":city,
            "disaster_type":disaster_type, 
            "disaster_description":disaster_description, 
            "comments":comments,
            "polygon_data": polygons_data, 
            "pre_path":pre_path, 
            "post_path":post_path, 
        })
        try:
            # Create and save an instance of JsonFileModel
            json_model_instance = JsonFileModel.objects.create(user=request.user, json_file=json_data)
            json_model_instance.save()
            messages.success(request, "JsonFileModel model created")
            return redirect("map")
        except:
            messages.error(request, "Unable to save inference")
            return redirect("inferenceform")
    else:
        return render(request, "app/inferenceform.html")
        


