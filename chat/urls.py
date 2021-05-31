from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views

# name of the app when calling it externally
app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path('<str:room_name>/', views.room, name='room'),
    
]