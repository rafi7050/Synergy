from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Message(models.Model):
    room = models.TextField(default="NA")  
    username = models.TextField(default="NA")  
    content = models.TextField(default="NA")  
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)




