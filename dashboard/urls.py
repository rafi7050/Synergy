from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

# name of the app when calling it externally
app_name = "dashboard"

urlpatterns = [
    path("", views.view_dashboard, name="view_dashboard"),
    
]