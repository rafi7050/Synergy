from django.urls import path
from report import views

# name of the app when calling it externally
app_name = "report"

urlpatterns = [
    path("", views.report_create, name="report_create"),
    path("open/", views.report_open, name="report_open"),
    ]