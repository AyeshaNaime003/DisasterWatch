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