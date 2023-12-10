# DisasterWatch

virtualenv env
pip install django
env/scripts/activate

make server:
django-admin startproject server ./
 
make app
django-admin startapp app

confugure the app in the settings
 "app.apps.AppConfig"

 make template dir alongside app and server
 configure so the server can see the template:   BASE_DIR/'templates' in setting.py

 pages:
 login,
 home,
 get sentinel2 imagery form,
 stats,
 map

 login: get to go to the page, post to sent form data to view, using django's builtin functions, authenticate the valid user and then login(create session id)