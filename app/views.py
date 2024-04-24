from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.forms.models import model_to_dict
from .models import CustomUser, JsonFileModel, InferenceModel
from django.http import JsonResponse
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
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from .forms import CustomUserForm
from django.template.loader import render_to_string

PIP_DEFAULT_TIMEOUT=100

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
server_dir = os.path.join(parent_dir, 'server')
model_dir = os.path.join(parent_dir, 'model')


sys.path.append(parent_dir)
sys.path.append(server_dir)
sys.path.append(model_dir)

# print(f"paths to check for module: {sys.path}")

from server.settings import *
from .model.data_preprocessing import tif_to_img, one_hot_encoding_mask, mask_to_polygons, get_tif_transform, pixels_to_coordinates


os.environ['TORCH_HOME'] = model_dir

def get_address(request):
    if request.method == 'GET':
        try:
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
            
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.reverse((lat, lon), exactly_one=True)
            print("1")
            return JsonResponse({'address': location.address})
        
        except GeocoderUnavailable:
            # Handle the exception
            messages.error(request, "Address retrieval failed. Please try again later.")
            return redirect("inferenceform")
        
    return JsonResponse({'error': 'Invalid request'})

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

def get_user_details(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)    
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'contact': user.contact,
        'is_admin': user.is_admin,
    })

@login_required(login_url="login/")
def adminPanel(request):
    users = CustomUser.objects.all()
    return render(request, "app/adminPanel.html", {'users': users})

@login_required(login_url="login/")
def addUser(request):
    if request.method == 'POST':
        print("form submitted")
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        fName = request.POST.get('firstName')
        lName = request.POST.get('lastName')
        is_admin = request.POST.get('is_admin') == 'on'  
        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password, first_name=fName, last_name=lName, contact=contact, is_admin=is_admin)
            messages.success(request, f"User '{username}' added successfully!")
        except Exception as e:
            messages.error(request, f"Failed to add user: {e}")
        finally:
            return redirect('admin-panel')
    else:
        return render(request, 'app/addUser.html')
    
@login_required(login_url="login/")
def edit_user(request, user_id):
    print("In edit function")
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        is_admin = request.POST.get('is_admin') == 'on'  
        user.is_admin = is_admin
        user.save()
        print("Role updated")
        messages.success(request, f"User '{user.username}' updated successfully!")
        return redirect('admin-panel')
    return redirect('admin-panel')

@login_required(login_url="login/")
def delete_user(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if user:
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully!")
    else:
        messages.error(request, "User not found!")
    return redirect('admin-panel')

@login_required(login_url="login/")
def map(request): 
    # get data from database
    json_file_model = JsonFileModel.objects.filter(user=request.user).last()
    # print(model_to_dict(json_file_model))
    json_data = json.loads(json_file_model.json_file)
    
    date = json_data.get("date")   
    city = json_data["city"]   
    state = json_data["state"]   
    country = json_data["country"]   
    disaster_type = json_data["disaster_type"]   
    disaster_description = json_data["disaster_description"]   
    comments = json_data["comments"]   
    pre_path = json_data["pre_path"]   
    post_path = json_data["post_path"]   
    map_middle_lat = json_data["map_middle_lat"]   
    map_middle_long = json_data["map_middle_long"]   
    polygon_data = json_data["polygon_data"]   
        
    context = {
        'date': date,
        'city': city,
        'state': state,
        'country': country,
        'disaster_type': disaster_type,
        'disaster_description': disaster_description,
        'comments': comments,
        'pre_path': pre_path,
        'post_path': post_path,
        'polygon_data': polygon_data,
        'map_middle_lat': map_middle_lat,
        'map_middle_long': map_middle_long,
    }
    # print(context)
    return render(request, 'app/map.html', context={'context': context})



@login_required(login_url="login/")
def dashboard(request):
    # json_file_model = JsonFileModel.objects.filter(user=request.user).last()
    # json_data = json.loads(json_file_model.json_file)
    
    # date = json_data.get("date")   
    # city = json_data["city"]   
    # state = json_data["state"]   
    # country = json_data["country"]   
    # disaster_type = json_data["disaster_type"]   
    # disaster_description = json_data["disaster_description"]   
    # comments = json_data["comments"]   
    # pre_path = json_data["pre_path"]   
    # post_path = json_data["post_path"]   
    # map_middle_lat = json_data["map_middle_lat"]   
    # map_middle_long = json_data["map_middle_long"]   
    # polygon_data = json_data["polygon_data"]   
        
    # context = {
    #     'date': date,
    #     'city': city,
    #     'state': state,
    #     'country': country,
    #     'disaster_type': disaster_type,
    #     'disaster_description': disaster_description,
    #     'comments': comments,
    #     'pre_path': pre_path,
    #     'post_path': post_path,
    #     'polygon_data': polygon_data,
    #     'map_middle_lat': map_middle_lat,
    #     'map_middle_long': map_middle_long,
    # }
    # return render(request, 'app/dashboard.html', context={'context': context})
    inference_model = InferenceModel.objects.filter(user=request.user).last()
    
    # context = {
    #     'id': inference_model.id if inference_model else None,
    #     'user': inference_model.user if inference_model else None,
    #     'disaster_date': inference_model.disaster_date if inference_model else None,
    #     'disaster_city': inference_model.disaster_city if inference_model else None,
    #     'disaster_state': inference_model.disaster_state if inference_model else None,
    #     'disaster_country': inference_model.disaster_country if inference_model else None,
    #     'disaster_type': inference_model.disaster_type if inference_model else None,
    #     'disaster_description': inference_model.disaster_description if inference_model else None,
    #     'disaster_comments': inference_model.disaster_comments if inference_model else None,
    #     'tif_middle_latitude': inference_model.tif_middle_latitude if inference_model else None,
    #     'tif_middle_longitude': inference_model.tif_middle_longitude if inference_model else None,
    #     'pre_tif_path': inference_model.pre_tif_path if inference_model else None,
    #     'post_tif_path': inference_model.post_tif_path if inference_model else None,
    #     'results': inference_model.results if inference_model else None,
    #     'created_at': inference_model.created_at if inference_model else None,
    #     'updated_at': inference_model.updated_at if inference_model else None
    # }
    return render(request, 'app/dashboard.html', {"context":inference_model})


@login_required(login_url="login/")
def profile(request):
    # get current user
    user = request.user
    print(user.email, user.first_name, user.last_name, user.contact, user.profile_picture.url if user.profile_picture else '')
    user_inferences = JsonFileModel.objects.filter(user=user)
    # print(user_inferences)
    # make chnages to the fields of current user using the form
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact-number')
        location = request.POST.get('location')
        profile_picture = request.FILES.get('profile_picture')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.contact = contact_number
        user.location = location

        # Check if profile picture exists
        if profile_picture:
            user.profile_picture.delete()
            user.profile_picture = profile_picture
            print("picture saved")

        # Save the changes
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    else:
        return render(request, "app/profile.html", context={'user': user, "user_inferences":user_inferences})


@login_required(login_url="login/")
def help(request):
    return render(request, "app/help.html")


# # @login_required(login_url="login/")
# def inferenceform(request):
#     if request.method == 'POST' and request.POST["comments"]=="EMPTY":
#             return redirect("dashboard")
#     if request.method == 'POST' and request.FILES.get('pre_image') != None and request.FILES.get('post_image') != None:
#         # get data from form 
#         pre_image = request.FILES.get('pre_image')
#         post_image = request.FILES.get('post_image')
#         city = request.POST['city']
#         date = request.POST['date']
#         disaster_type = request.POST['disaster_type']
#         disaster_description = request.POST['disaster_description']
#         comments = request.POST['comments']

#         # save the tiff files temporarily in media root
#         file_name = f"{date}_{city}_{disaster_type}"
#         pre_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_pre.tif")
#         post_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_post.tif")
#         with open(pre_path, 'wb') as f: 
#             for chunk in pre_image.chunks():
#                 f.write(chunk)
#         with open(post_path, 'wb') as f:
#             for chunk in post_image.chunks():
#                 f.write(chunk)
#         print("pre and post tifs saved")
        
#         # convert the tiff files to RGB images to run for inference
#         pre_tif, post_tif = gdal.Open(pre_path), gdal.Open(post_path)
#         pre_image, post_image = torch.from_numpy(tif_to_img(pre_tif)), torch.from_numpy(tif_to_img(post_tif))
#         pre_post = torch.cat((pre_image, post_image), dim=2).permute(2,0,1).unsqueeze(0).to(torch.float)
#         print(f"Tifs converted to concatenated images of {pre_post.shape}, {pre_post.dtype}")
#         # INFERENCE------------------------------------------------------------------
#         # model = SeResNext50_Unet_MultiScale()
#         # output = model(pre_post)
       
#         # DUMMY DATA----------------------------------------------------------------------
#         dummy_mask = cv2.imread("woolsey-fire_00000715_post_disaster.png") 
#         print(f"Dummy mask shape an type {dummy_mask.shape}, {dummy_mask.dtype}")
#         dummy_masks = one_hot_encoding_mask(dummy_mask)
#         print(f"Dummy mask after hot encoding  {dummy_masks.shape}, {dummy_masks.dtype}")
#         tranform = get_tif_transform(pre_path)
#         classes=["red","orange","yellow","green"]
        
#         # format the inference for database
#         polygons_data={}
#         for i, mask in enumerate(dummy_masks):
#             color=classes[i]
#             _, mask = cv2.threshold(mask.astype('uint8'), 0, 255, cv2.THRESH_BINARY)
#             polygons_in_mask = mask_to_polygons(mask, tranform, rdp=False)
#             print(f"{color}: {len(polygons_in_mask)}")
#             polygons_data[color]=polygons_in_mask
#         # Convert the dictionary to JSON format
#         print(request.POST['city'])
#         print( polygons_in_mask[0]['address']['city'])
#         print( polygons_in_mask[0]['address']['town'])
#         transform = get_tif_transform(pre_path)
#         map_middle_lat, map_middle_long = pixels_to_coordinates(transform, (612,612))
#         json_data = json.dumps({
#             "date": date,
#             "city": polygons_in_mask[0]['address']['city'] if polygons_in_mask[0]['address']['city'] == request.POST['city'] else polygons_in_mask[0]['address']['town'],
#             "state":polygons_in_mask[0]['address']['state'],
#             "country":polygons_in_mask[0]['address']['country'],
#             "disaster_type":disaster_type, 
#             "disaster_description":disaster_description, 
#             "comments":comments,
#             'map_middle_lat': map_middle_lat,
#             'map_middle_long': map_middle_long,
#             "pre_path":pre_path, 
#             "post_path":post_path,
#             "polygon_data": polygons_data, 
#         })
#         try:
#             # Create and save an instance of JsonFileModel
#             json_model_instance = JsonFileModel.objects.create(user=request.user, json_file=json_data)
#             json_model_instance.save()
#             print("JsonFileModel model created")
#             messages.success(request, "JsonFileModel model created")
#             return redirect("dashboard")
#         except:
#             print("Unable to save inference")
#             messages.error(request, "Unable to save inference")
#             return redirect("inferenceform")
#     else:
#         return render(request, "app/inferenceform.html")
        
@login_required(login_url="login/")
def inferenceform(request):
    if request.method == 'POST' and request.FILES.get('pre_image') and request.FILES.get('post_image'):
        # Get data from form
        pre_image = request.FILES['pre_image']
        post_image = request.FILES['post_image']
        disaster_city = request.POST['city']
        disaster_date = request.POST['date']
        disaster_type = request.POST['disaster_type']
        disaster_description = request.POST['disaster_description']
        disaster_comments = request.POST['comments']
        # Save the tiff files temporarily in media root
        file_name = f"{disaster_date}_{disaster_city}_{disaster_type}"
        pre_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_pre.tif")
        post_path = os.path.join(MEDIA_ROOT, 'tiff', file_name+"_post.tif")
        with open(pre_path, 'wb') as f:
            for chunk in pre_image.chunks():
                f.write(chunk)
        with open(post_path, 'wb') as f:
            for chunk in post_image.chunks():
                f.write(chunk)
        print("Pre and post tifs saved")
        # Convert the tiff files to RGB images to run for inference
        pre_tif, post_tif = gdal.Open(pre_path), gdal.Open(post_path)
        pre_image, post_image = torch.from_numpy(tif_to_img(pre_tif)), torch.from_numpy(tif_to_img(post_tif))
        pre_post = torch.cat((pre_image, post_image), dim=2).permute(2,0,1).unsqueeze(0).to(torch.float)
        print(f"Tifs converted to concatenated images of {pre_post.shape}, {pre_post.dtype}")
        # Dummy data (for testing purposes)
        dummy_mask = cv2.imread("woolsey-fire_00000715_post_disaster.png")
        print(f"Dummy mask shape and type {dummy_mask.shape}, {dummy_mask.dtype}")
        dummy_masks = one_hot_encoding_mask(dummy_mask)
        print(f"Dummy mask after hot encoding {dummy_masks.shape}, {dummy_masks.dtype}")
        transform = get_tif_transform(pre_path)
        classes = ["red", "orange", "yellow", "green"]
         # Format the inference data for the database
        results = {}
        for i, mask in enumerate(dummy_masks):
            color = classes[i]
            _, mask = cv2.threshold(mask.astype('uint8'), 0, 255, cv2.THRESH_BINARY)
            polygons_in_mask = mask_to_polygons(mask, transform, rdp=False)
            print(f"{color}: {len(polygons_in_mask)}")
            results[color] = polygons_in_mask
        # Convert the dictionary to JSON format
        tif_middle_latitude, tif_middle_longitude = pixels_to_coordinates(transform, (612, 612))
        try:
            # Create and save an instance of InferenceModel
            inference_model_instance = InferenceModel.objects.create(
                user=request.user,
                disaster_date=disaster_date,
                disaster_city=polygons_in_mask[0]['address']['city'] if polygons_in_mask[0]['address']['city'] == request.POST['city'] else polygons_in_mask[0]['address']['town'],
                disaster_state=polygons_in_mask[0]['address']['state'],
                disaster_country=polygons_in_mask[0]['address']['country'],
                disaster_type=disaster_type,
                disaster_description=disaster_description,
                disaster_comments=disaster_comments,
                tif_middle_latitude=tif_middle_latitude,
                tif_middle_longitude=tif_middle_longitude,
                pre_tif_path=pre_path,
                post_tif_path=post_path,
                results=results,
            )
            inference_model_instance.save()
            print("InferenceModel model created")
            messages.success(request, "InferenceModel model created")
            return redirect("dashboard")
        except Exception as e:
            print(f"Unable to save inference: {e}")
            messages.error(request, "Unable to save inference")
            return redirect("inferenceform")
    else:
        return render(request, "app/inferenceform.html")