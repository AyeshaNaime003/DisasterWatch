from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests

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
    return render(request, "app/profile.html")

def help(request):
    return render(request, "app/help.html")

def notifications(request):
    return render(request, "app/notifications.html")

def settings(request):
    return render(request, "app/settings.html")