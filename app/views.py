from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests

# Create your views here.
@login_required(login_url="login/")
def home(request):
    api_url = "https://api.reliefweb.int/v1/reports?appname=apidoc&preset=latest&query[value]=earthquake&limit=5"
    response = requests.get(api_url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        api_data = response.json()        
        reports = api_data.get("data", [])    
        print(reports)    
        return render(request, 'app/home.html', {'reports': reports})
    else:
        # Handle the error gracefully
        error_message = f"Failed to fetch data from API. Status code: {response.status_code}"
        return render(request, 'app/home.html', {'error_message': error_message})

def about(request):
    return render(request, "app/about.html")

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
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "app/login.html")

@login_required(login_url="login/")
def logoutPage(request):
    logout(request)
    return redirect("login")

def map(request):
    return render(request, "app/map.html")