from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "dist/welcome_page.html")

def company(request):
    return render(request, "dist/about.html")  

def company_contact(request):
    return render(request, "dist/contact.html")  

def company_thankyou(request):
    return render(request, "dist/thankyou.html")  

def vision(request):
    return render(request, "dist/vision.html") 

def vision_system(request):
    return render(request, "dist/system.html")  


