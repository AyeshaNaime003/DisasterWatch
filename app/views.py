from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser,InferenceModel, LoginHistoryModel
from django.http import JsonResponse
from django.utils import timezone
import json
import os
import torch
import json
from server.settings import *
from .inference.preprocessing import *
from .inference.postprocessing import *
from .inference.datastorage import *
from .inference.models import BASE_Transformer_UNet
from .api import *
from django.urls import reverse
from django.http import HttpResponse
from math import pi, cos, radians, atan2
from importlib.machinery import SourceFileLoader
import pdfkit
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
import rasterio

cwd = os.getcwd()
model_dir = os.path.join(cwd, "app", "inference")
bitmodule = SourceFileLoader('bitmodule', os.path.join(model_dir, "bit_resnet.py")).load_module()



def loginPage(request):
    # login the use in
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
            print("LOGIN SUCCESSFUL, LOGIN HISTORY CREATED")
            return redirect('home')
        else: 
            messages.error(request, "Invalid credentials")
            return redirect("login")
    # showing the login page
    else:
        messages.error(request, None)
        return render(request, "app/login.html")
    

@login_required(login_url="login/")
def home(request):
    print(f"Welcome to home page {request.user.username}")
    api_response, reports = get_news()
    if reports:
        return render(request, 'app/home.html', {'reports': reports})
    else:
        messages.error(request, f"Failed to fetch data from API. Status code: {api_response.status_code}")
        return render(request, 'app/home.html')


@login_required(login_url="login/")
def logoutPage(request):
    logout(request)
    print("logout")
    print(request.user.is_authenticated)
    return redirect("login")


def get_user_details(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)    
    loginHistory = LoginHistoryModel.objects.filter(user=user).values('login_time')
    formatted_history = []
    for history in loginHistory:
        formatted_history.append({
            'login_time': history['login_time'].strftime('%Y/%m/%d %H:%M:%S'),
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
        is_admin = bool(request.POST.get('is_admin') )
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
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        is_admin = request.POST.get('is_admin') == 'on'  
        user.is_admin = is_admin
        user.save()
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
def profile(request):
    # get current user
    user = request.user
    print(user.email, user.first_name, user.last_name, user.contact, user.profile_picture.url if user.profile_picture else '')
    user_inferences = InferenceModel.objects.filter(user=user).order_by('-created_at')
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
def map_with_id(request, inference_id): 
    # get the inference model with the id else send error
    inference_model = InferenceModel.objects.filter(user=request.user, id=inference_id).last()
    if not inference_model:
        return HttpResponse("Inference model not found", status=404)
    else:
        results = json.loads(inference_model.results)
        classes = ["green", "yellow", "orange", "red"]
        classes_count = [len(results[cls]) for cls in classes]
        print(f"Classes count: {classes_count}")
        address_components = None
        if sum(classes_count) > 0:
            address_components = [
                results[color][0]["address"].keys() 
                for color in results.keys() 
                if len(results[color]) > 0][0]
            address_components=list(address_components)
        print(f"address cmponents: {address_components}")

        weather = request.session.get('weather')
        population = request.session.get('population')

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
            "address_components": address_components, 
            'weather': weather,
            'population': population,

        }})


def get_critically_damaged_areas(results, address_components):
    all_addresses = [point["address"] for color in results.keys() for point in results[color]]
    for index, component in enumerate(address_components):
        presentInAll=all([True if component in address.keys() else False for address in all_addresses])
        if not presentInAll:
            continue
        uniqueValues=len({address[component] for address in all_addresses})>1
        if presentInAll and uniqueValues:
            break
    chosen_component = address_components[index]
    unique_addresses = [point["address"][chosen_component] for color_points in results.values() for point in color_points if chosen_component in point["address"]]
    
    # getting the number of each class in each unique value of the bet component
    componentDict = {address: {"red":0,
                    "orange":0, 
                    "yellow":0, 
                    "green":0} for address in unique_addresses}
    
    for color in results.keys():
        for point in results[color]:
            if chosen_component in point["address"].keys():
                address = point["address"][chosen_component]
                componentDict[address][color]+=1

    for address, dictionary in componentDict.items():
        rating = 3*dictionary["red"]+2*dictionary["orange"]+dictionary["yellow"]
        componentDict[address]["rating"]=rating
    
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
        }
        sortedComponentRevised.append(componentData_formatted)
    return sortedComponentRevised, chosen_component


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

def get_address_components(results, classes_count):
    address_components = None
    if sum(classes_count)>0:
        if classes_count[0]>0:
            address_components = list(results["green"][0]["address"].keys())
        elif classes_count[1]>0:
            address_components = list(results["yellow"][0]["address"].keys())
        elif classes_count[2]>0:
            address_components = list(results["orange"][0]["address"].keys())
        else:
            address_components = list(results["red"][0]["address"].keys())
    return address_components


@login_required(login_url="login/")
def dashboard_with_id(request, inference_id):
    # get the inference model with the id else send error
    inference_model = InferenceModel.objects.filter(user=request.user, id=inference_id).last()
    if not inference_model:
        return HttpResponse("Inference model not found", status=404)
    else:
        # get results
        results = json.loads(inference_model.results)
        # get the classes count form the results
        classes = ["green", "yellow", "orange", "red"]
        classes_count = [len(results[cls]) for cls in classes]
        print(f"Classes count: {classes_count}")
        # Damage area data: critisally damaged areas and total damaged area
        totalDamagedBuildings = classes_count[1]+classes_count[2]+ classes_count[3]
        if totalDamagedBuildings>0:
            boundary_coordinates = get_extreme_points([(point["center_lat"], point["center_long"]) for color, points in results.items() if color != "green" for point in points])
            sorted_critically_damaged_areas, chosen_component = get_critically_damaged_areas(results, get_address_components(results, classes_count))
            chosen_component = chosen_component.capitalize()
            total_damaged_area = int(area_calculator(boundary_coordinates))/ 1e6 if totalDamagedBuildings>3 else 0
        else: 
            boundary_coordinates, sorted_critically_damaged_areas, chosen_component = None, None, None
            total_damaged_area = 0
        # formatting the data for api calls
        disaster_time = inference_model.disaster_date.strftime('%Y/%m/%d') if inference_model.disaster_date else None
        disaster_city = inference_model.disaster_city
        disaster_state = inference_model.disaster_state
        weather = get_weather(disaster_city if disaster_city else disaster_state, date_str=disaster_time)
        population = get_population(disaster_city if disaster_city else disaster_state)
        request.session['weather'] = weather
        request.session['population'] = population
        
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
            'weather': weather if weather is not None else {},
            'population': population if population is not None else "None",
            'building_count': sum(classes_count),
            'damaged_count': sum(classes_count[1:]),
            'graph_data': classes_count,
            'boundary_coordinates': boundary_coordinates,
            "disaster_areas": sorted_critically_damaged_areas,
            "chosen_component": chosen_component, 
            "total_damaged_area": total_damaged_area, 
            }
        })

def tiff_has_geospatial_info(tiff_path):
    try:
        with rasterio.open(tiff_path) as dataset:
            # Check if the TIFF file has geospatial information
            return dataset.crs is not None
    except Exception as e:
        print(f"Error checking geospatial info: {e}")
    return False


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
        print("Pre and post tifs saved in media")

        if not (tiff_has_geospatial_info(pre_path) and tiff_has_geospatial_info(post_path)):
            messages.error(request, "Uploaded TIFF files do not contain geospatial information.")
            print("Uploaded TIFF files do not contain geospatial information")
            return redirect("inferenceform")

        # convert to image
        pre_image, post_image = tif_to_img(pre_path, post_path)
        print(pre_image.shape)
        print(type(pre_image))
        h, w = post_image.shape[0], post_image.shape[1]
        
        # model and inference
        device = "cuda" if torch.cuda.is_available() else "cpu"
        loaded_model = BASE_Transformer_UNet(input_nc=3, 
                                            output_nc=5, 
                                            token_len=4, 
                                            resnet_stages_num=4,
                                            with_pos='learned', 
                                            enc_depth=1, 
                                            dec_depth=8).to(device)

        loaded_model.load_state_dict(torch.load(os.path.join(model_dir, "checkpoint.pth"), map_location=torch.device('cpu')))
        processed_output_masks, inference_time, postprocessing_time = postprocessing(pre_image, post_image, loaded_model)
        print(f"Model Inference Time: {inference_time} seconds")
        print(f"Preprocessing Time: {postprocessing_time} seconds")

        
        # data storage
        start = time.time()
        transform = get_tif_transform(pre_path)
        classes = ['green', 'yellow', 'orange', 'red']
        results={}

        # mask_address = None
        for index, mask in enumerate(processed_output_masks[1: ]):
            color = classes[index]
            polygons_in_mask = get_polygons(mask, transform, rdp=False)
            color_count = len(polygons_in_mask)
            print(f"{color}: {color_count}")
            results[color] = polygons_in_mask
        print()
        end = time.time()
        addressing_time = end-start
        print(f"Addressing Time: {addressing_time} seconds")
        
        # middle of the tiff files to be the centre of the map
        tif_middle_latitude, tif_middle_longitude = pixels_to_coordinates(transform, (h/2, w/2))
        middle_address = get_address(tif_middle_latitude, tif_middle_longitude)
        print(f"middle address: {(tif_middle_latitude, tif_middle_longitude, middle_address)}")
        if middle_address:
            disaster_city = middle_address.get("city", disaster_city) 
            disaster_state = middle_address.get("state")
            disaster_country = middle_address["country"]
        else:
            disaster_city, disaster_state, disaster_country = disaster_city, "", ""
        try:
            # Create and save an instance of InferenceModel
            inference_model_instance = InferenceModel.objects.create(
                user = request.user,
                disaster_date = disaster_date,
                disaster_city =  disaster_city,
                disaster_state = disaster_state,
                disaster_country = disaster_country,
                disaster_type = disaster_type,
                disaster_description = disaster_description,
                disaster_comments = disaster_comments,
                tif_middle_latitude = tif_middle_latitude,
                tif_middle_longitude = tif_middle_longitude,
                pre_tif_path = pre_path,
                post_tif_path = post_path,
                results = json.dumps(results),
            )
            inference_model_instance.save()
            print("InferenceModel model created")
            messages.success(request, "InferenceModel model created")
            return redirect(reverse('dashboard_with_id', kwargs={'inference_id': inference_model_instance.id}))
        except Exception as e:
            print(f"Unable to save inference: {e}")
            messages.error(request, "Unable to save inference")
            return redirect("inferenceform")
    else:
        return render(request, "app/inferenceform.html")










