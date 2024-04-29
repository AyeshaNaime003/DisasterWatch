from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser, InferenceModel, LoginHistoryModel
from django.http import JsonResponse
from django.utils import timezone
import json
import requests
import os
import sys
from PIL import Image
import torch
from osgeo import gdal
import cv2
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from server.settings import *
from .model.data_preprocessing import tif_to_img, one_hot_encoding_mask, mask_to_polygons, get_tif_transform, pixels_to_coordinates
from .api import get_weather, get_population, get_news
from django.urls import reverse
from django.http import HttpResponse
from math import pi, cos, radians, atan2









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
            LoginHistoryModel.objects.create(user=user, login_time=timezone.now())
            print("LOGIN SUCCESSFUL, LOGINHISTORY CREATED")
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
    
    reports = get_news()
    if reports:
        return render(request, 'app/home.html', {'reports': reports})
    else:
        messages.error(request, f"Failed to fetch data from API. Status code: {api_response.status_code}")
        return render(request, 'app/home.html')


@login_required(login_url="login/")
def logoutPage(request):
    login_history = LoginHistoryModel.objects.filter(user=request.user).order_by('-login_time').first()
    if login_history:
        login_history.logout_time = timezone.now()
        login_history.save()
        print()
    logout(request)
    print("logout")
    return redirect("login")


def get_user_details(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)    
    loginHistory = LoginHistoryModel.objects.filter(user=user).values('login_time', 'logout_time')
    formatted_history = []
    for history in loginHistory:
        formatted_history.append({
            'login_time': history['login_time'].strftime('%Y/%m/%d %H:%M:%S'),
            'logout_time': history['logout_time'].strftime('%Y/%m/%d %H:%M:%S') if history['logout_time'] else "Still logged in"
        })
    print(formatted_history)
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'contact': user.contact,
        'is_admin': user.is_admin,
        'login_history':formatted_history
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


def get_critically_damaged_areas(results):
    unique_addresses={
    "towns":{point["address"]["town"] for color_points in results.values() for point in color_points}, 
    "suburbs":{point["address"]["suburb_municipality"] for color_points in results.values() for point in color_points},
    "roads":{point["address"]["road"] for color_points in results.values() for point in color_points}
}
    # selecting the best component
    best_component = max(
    ("towns", len(unique_addresses["towns"])),
    ("suburbs", len(unique_addresses["suburbs"])),
    ("roads", len(unique_addresses["roads"])),key=lambda x: x[1])[0]
    print(best_component)
    # getting the number of each class in each unique value of the bet component
    componentDict = {road: {"red":0,
                    "orange":0, 
                    "yellow":0, 
                    "green":0} for road in unique_addresses[best_component]}
    for color in results.keys():
        for point in results[color]:
            road = point["address"]["road"]
            componentDict[road][color]+=1
    for road, dictionary in componentDict.items():
        rating = 3*dictionary["red"]+2*dictionary["orange"]+dictionary["yellow"]
        componentDict[road]["rating"]=rating
    sortedComponent = dict(sorted(componentDict.items(), key=lambda x: x[1]['rating'], reverse=True))
    sortedComponentRevised = []
    for componentName, componentData in sortedComponent.items():
        componentData_formatted = {
            'index': len(sortedComponentRevised) + 1,
            'componentName': componentName,
            'red': componentData['red'],
            'orange': componentData['orange'],
            'yellow': componentData['yellow'],
            'green': componentData['green'],
            'rating': componentData['rating']
            # Add more data if needed
        }
        sortedComponentRevised.append(componentData_formatted)
    return sortedComponentRevised


def get_extreme_points(coordinates):
   # Define a reference point (e.g., the center of the polygon)
    reference_point = (sum(coord[0] for coord in coordinates) / len(coordinates),
                       sum(coord[1] for coord in coordinates) / len(coordinates))

    # Define a custom key function to calculate the polar angle from the reference point
    def polar_angle(coord):
        dy = coord[0] - reference_point[0]
        dx = coord[1] - reference_point[1]
        return (atan2(dy, dx) + 2 * pi) % (2 * pi)  # Ensure angle is in the range [0, 2*pi)

    # Sort the coordinates in clockwise order based on the polar angle from the reference point
    sorted_coordinates = sorted(coordinates, key=polar_angle, reverse=True)
    nested_lists = [[coord[0], coord[1]] for coord in sorted_coordinates]

    return nested_lists


EARTH_RADIUS_IN_METERS = 6378137
EARTH_CIRCUMFERENCE_IN_METERS = 2 * EARTH_RADIUS_IN_METERS * pi
def area_calculator(points):
    area = None
    if points and len(points) > 2:
        p0 = points[0]
        new_points = []
        for p in points[1:]:
            y = (p[0] - p0[0]) / 360 * EARTH_CIRCUMFERENCE_IN_METERS
            x = (p[1] - p0[1]) / 360 * EARTH_CIRCUMFERENCE_IN_METERS * cos(radians(p[0]))
            new_points.append({'x': x, 'y': y})
        
        if new_points and len(new_points) > 1:
            area = 0
            for i in range(len(new_points) - 1):
                p1 = new_points[i]
                p2 = new_points[i+1]
                area += ((p1['y'] * p2['x']) - (p1['x'] * p2['y'])) / 2
            area = abs(area)
    return area


@login_required(login_url="login/")
def dashboard_with_id(request, inference_id):
    # get the inference model with the id else send error
    inference_model = InferenceModel.objects.filter(user=request.user, id=inference_id).last()
    if not inference_model:
        return HttpResponse("Inference model not found", status=404)
    else:
        # formatting the data for api calls
        disaster_time = inference_model.disaster_date.strftime('%Y/%m/%d') if inference_model.disaster_date else None
        disaster_city = inference_model.disaster_city
        results = json.loads(inference_model.results)
        # weather
        # weather = get_weather(disaster_city, date_str=disaster_time)
        weather = {
            "city": "hehe",
            "description": "hehe",
            "temperature": "hehe",
            "wind": "hehe",
            "humidity": "hehe",
            "rain": "hehe",
            "clouds": "hehe"
        }
        # population
        # population = get_population(disaster_city)
        boundary_coordinates = get_extreme_points([(point["center_lat"], point["center_long"]) for color, points in results.items() if color != "green" for point in points])
        print(boundary_coordinates)

        # chart
        classes = ["green", "yellow", "orange", "red"]
        classes_count = [len(results[cls]) for cls in classes]
        class_none = [0, 0, 0, 0]

        # data to send to front end
        return render(request, 'app/dashboard.html', {"context": {
            'inference_id': inference_model.id,
            'disaster_date': disaster_time,
            'disaster_city': disaster_city,
            'disaster_state': inference_model.disaster_state,
            'disaster_country': inference_model.disaster_country,
            'disaster_type': inference_model.disaster_type,
            'disaster_description': inference_model.disaster_description,
            'tif_middle_latitude': inference_model.tif_middle_latitude,
            'tif_middle_longitude': inference_model.tif_middle_longitude,
            'results': json.loads(inference_model.results),
            'weather': weather,
            'population': "None",
            'building_count': sum(classes_count),
            'damaged_count': sum(classes_count[1:]),
            'graph_data': classes_count if results else class_none,
            "disasterAreas": get_critically_damaged_areas(results),
            "boundary_coordinates": boundary_coordinates, 
            "total_damaged_area": int(area_calculator(boundary_coordinates))/ 1e6 
            }
        })


@login_required(login_url="login/")
def map_with_id(request, inference_id): 
    # get the inference model with the id else send error
    inference_model = InferenceModel.objects.filter(user=request.user, id=inference_id).last()
    if not inference_model:
        return HttpResponse("Inference model not found", status=404)
    else:
        return render(request, 'app/map.html', {"context":{
            'disaster_date': inference_model.disaster_date.strftime('%Y-%m-%d') if inference_model and inference_model.disaster_date else None,
            'disaster_city': inference_model.disaster_city if inference_model else None,
            'disaster_state': inference_model.disaster_state if inference_model else None,
            'disaster_country': inference_model.disaster_country if inference_model else None,
            'disaster_type': inference_model.disaster_type if inference_model else None,
            'disaster_description': inference_model.disaster_description if inference_model else None,
            'tif_middle_latitude': inference_model.tif_middle_latitude if inference_model else None,
            'tif_middle_longitude': inference_model.tif_middle_longitude if inference_model else None,
            'results': json.loads(inference_model.results) if inference_model else None,
        }})


@login_required(login_url="login/")
def profile(request):
    # get current user
    user = request.user
    print(user.email, user.first_name, user.last_name, user.contact, user.profile_picture.url if user.profile_picture else '')
    user_inferences = InferenceModel.objects.filter(user=user).order_by('-created_at')
    print(user_inferences)
    # make changes to the fields of current user using the form
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
                results=json.dumps(results),
            )
            inference_model_instance.save()
            print("InferenceModel model created")
            messages.success(request, "InferenceModel model created")
            dashboard_url = reverse('dashboard_with_id', kwargs={'inference_id': inference_model_instance.id})
            return redirect(dashboard_url)
        except Exception as e:
            print(f"Unable to save inference: {e}")
            messages.error(request, "Unable to save inference")
            return redirect("inferenceform")
    else:
        return render(request, "app/inferenceform.html")
    






"""

@login_required(login_url="login/")
def dashboard(request):
    inference_model = InferenceModel.objects.filter(user=request.user).last()
    disaster_time = inference_model.disaster_date.strftime('%Y/%m/%d') if inference_model and inference_model.disaster_date else None
    print(disaster_time )
    disaster_city = inference_model.disaster_city if inference_model else None
    # weather = get_weather(disaster_city, date_str=disaster_time)
    weather = {
        "city":"hehe",
        "description":"hehe",
        "temperature":"hehe",
        "wind":"hehe",
        "humidity":"hehe",
        "rain": "hehe",
        "clouds":"hehe"
    }
    # population = get_population(disaster_city)
    # print(population)

    # data for the graphs
    json_graph_data = json.loads(inference_model.results)
    classes = ["green", "yellow", "orange", "red"]
    classes_count = []
    
    for i, cls in enumerate(classes): 
        # print(len(json_graph_data["red"]))
        classes_count.append(len(json_graph_data[cls]))
    print(classes_count)
    class_none = [0, 0, 0, 0]

    return render(request, 'app/dashboard.html', {"context":{
        'disaster_date': disaster_time,
        'disaster_city': disaster_city,
        'disaster_state': inference_model.disaster_state if inference_model else None,
        'disaster_country': inference_model.disaster_country if inference_model else None,
        'disaster_type': inference_model.disaster_type if inference_model else None,
        'disaster_description': inference_model.disaster_description if inference_model else None,
        'tif_middle_latitude': inference_model.tif_middle_latitude if inference_model else None,
        'tif_middle_longitude': inference_model.tif_middle_longitude if inference_model else None,
        'results': json.loads(inference_model.results) if inference_model else None,
        'weather':weather, 
        'population': "None", 
        'building_count': sum(classes_count),
        'damaged_count': sum(classes_count[1:]),
        'graph_data': classes_count if json_graph_data else class_none,
    }})

    

@login_required(login_url="login/")
def map(request): 
    inference_model = InferenceModel.objects.filter(user=request.user).last()
    return render(request, 'app/map.html', {"context":{
        'disaster_date': inference_model.disaster_date.strftime('%Y-%m-%d') if inference_model and inference_model.disaster_date else None,
        'disaster_city': inference_model.disaster_city if inference_model else None,
        'disaster_state': inference_model.disaster_state if inference_model else None,
        'disaster_country': inference_model.disaster_country if inference_model else None,
        'disaster_type': inference_model.disaster_type if inference_model else None,
        'disaster_description': inference_model.disaster_description if inference_model else None,
        'tif_middle_latitude': inference_model.tif_middle_latitude if inference_model else None,
        'tif_middle_longitude': inference_model.tif_middle_longitude if inference_model else None,
        'results': json.loads(inference_model.results) if inference_model else None,
    }})


"""












