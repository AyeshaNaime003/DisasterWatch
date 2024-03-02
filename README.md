# DisasterWatch

virtualenv env
pip install django
env/scripts/activate

make server:
django-admin startproject server ./
 
make app->frontend
django-admin startapp app

confugure the app in the settings
"app.apps.AppConfig"

make template dir alongside app and server
configure so the server can see the template:   BASE_DIR/'templates' in setting.py
will house index.html which load main css file and extend different templates

pages:
login_>authenticate, login(carries user info)
home->sidebar,[LINKS NOT WORKING]
get sentinel2 imagery form,
stats,
map

static dir in the main project dir, will house css files and assets
configure to project using static file dirs in settings.py
link to template file using {load static} and <link href="{% static '/styles/login.css' %}" rel="stylesheet"/>


login: get to go to the page, post to sent form data to view, using django's builtin functions, authenticate the valid user and then login(create session id)

news api: reliefweb, no ai key, just use get url to get news related to certain topics, rn only doing earthquakes, latest first

map api: 
 2) plotly: real time, satellite style using mapbox token, draw polygons, hover in the midpoint
geopy to get address from the latitude and lonitude of the polygon midpoint, display only landmark(if any) and street name
from the tiff file get the top left lat and lon, use these to calculate the affine trasnform matrix, xy->lan and lon, draw polygons


SUGGESTIONS:
home page links not working
let user toggle between two styles of map viewing: satellite and open-street-map
ISSUES:
page wont load until all the addressses are retrived