from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from knowledge.models import Industry, Value_chain, SDG

# directory path when uploading a profile picture related to a profile
def profile_pic_directory_path(user, filename):
   return 'profile_pic/{0}/{1}'.format(user.id, filename)


"""
----------------------- Model supporting the Profile --------------------------------------
The tuple TYPES and the models Capabilities and Country:
- TYPES: Tuple that list all the possible type an user can have
- Capabilities: Model that holds all the possible capabilites an user can have
- Country: Model that holds all the possible countries an user can be from
-------------------------------------------------------------------------------------------
"""

# Types of users - since a onetomany relation not need to have a model
TYPES = (
    ("1", "Governement"),
    ("2", "NGOs"),
    ("3", "Social Venture"),
    ("4", "Organization"),
    ("5", "Financial Institution"),
    ("6", "University"),
    ("7", "Experts"),
    ("8", "Platform Monitors"),
    ("9", "Others"),)

# Repository of all possible capabilities for an user
class Capabilities(models.Model):
    title = models.CharField(max_length=50, unique=True)
    contenu = models.TextField(default="NA")

    def __str__(self):
        return self.title

# Repository of all possible capabilities for an user
class Country(models.Model):
    index = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

"""
----------------------- Model for Profile --------------------------------------
The class Profile and it's related models:
- Profile: Model to hold all the information relative to an user - information (id - user - company_name - website - position_of_user - description - certification - type_user - profile_picture)
    + manytomany models (SDG - VC - IND - CAP - COUN)
- Follower: Model to show which user is following who, manytomany relationships => add_to_class to connect to User class
- Feedback: Model to show the feedback provided from an user to another, manytomany relationships => add_to_class to connect to User class
-------------------------------------------------------------------------------------------
"""
class Profile(models.Model):
    id = models.CharField(max_length=50, primary_key= True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=300, blank=True)
    position_of_user = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=150,default="NA")
    certification = models.BooleanField(default=False)
    type_user = models.CharField(max_length=30, choices=TYPES, default="9")
    profile_picture = models.ImageField(upload_to=profile_pic_directory_path,default="Null")
    country = models.ManyToManyField(Country, through="Country_User")
    capabilities = models.ManyToManyField(Capabilities, through="Capabilities_User")
    value_chain = models.ManyToManyField(Value_chain, through="Value_Chain_User")
    industry = models.ManyToManyField(Industry, through="Industry_User")
    sdg = models.ManyToManyField(SDG, through="SDG_User")


#create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, id=instance.id)


#save a profile when a user is created
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    
    instance.profile.save()


class Follower(models.Model):
    user_from = models.ForeignKey(User, related_name='user_from', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='user_to', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)
        def __str__(self):
            return '{} follows {}'.format(self.user_from, self.user_to)

# connect to user
User.add_to_class("following", models.ManyToManyField('self', through=Follower, related_name="followers", symmetrical=False))


class Feedback(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

# connect to user
User.add_to_class("feedback", models.ManyToManyField('self', through=Feedback, related_name="feedback_giver", symmetrical=False))


"""
----------------------- Model for Classifier --------------------------------------
The class SDG - VC - IND - CAP - COUN are used to classify the profile
- SDG_User: Model for the relation between SDG and User
- VC_User: Model for the relation between VC and User
- IND_User: Model for the relation between IND and User
- Capabilities_User: Model for the relation between CAP and User
- Country_User: Model for the relation between Country and User

For all the self.title is specified to return the title when the object is called
------------------------------------------------------------------------------------

"""

class Capabilities_User(models.Model):
    capabilities = models.ForeignKey(Capabilities, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Value_Chain_User(models.Model):
    value_chain = models.ForeignKey(Value_chain, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Industry_User(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)


class SDG_User(models.Model):
    sdg = models.ForeignKey(SDG, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Country_User(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)

"""
----------------------- Model for Interactions --------------------------------------
The class LF is used to structure the interactions on the platform specific to user
- LF: Model that show which users likes which feedback 
- DF: Model that show which users dislikes which feedback 
-------------------------------------------------------------------------------------
"""

class Liked_Feedback(models.Model):
    feedback_related = models.ForeignKey(Feedback,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Disliked_Feedback(models.Model):
    feedback_related = models.ForeignKey(Feedback,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)






