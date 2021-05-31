from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Message

@login_required
def index(request):
    return render(request, "dist/inside/chat/index.html")


@login_required
def room(request, room_name):
    username = request.GET.get('username', 'Anonymous')
    room_names = Message.objects.filter(room__contains=username).values_list("room", flat= True).distinct()
    messages = Message.objects.filter(room=room_name)

    return render(request, "dist/inside/chat/room.html", {'room_names': room_names, 'room_name': room_name, 'username': username, 'messages': messages})