from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify 
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager


# directory path when uploading a profile picture related to a profile
def profile_seed_directory_path(slug, filename):
   return 'seed_pic/{0}/{1}'.format(slug, filename)


# directory path when uploading a document related to a specific seed
def user_directory_path(seed_related,filename):
    return 'seed/{0}/{1}'.format(seed_related.id, filename)


#choices for the aim of a seed or vision
Aims = (
    ("1", "To raise awarness"),
    ("2", "To share a product or service"),
    ("3", "To search for improvement"),
    ("4", "To present theoretical results "),
    ("5", "To make laugh"),
    ("6", "Others"),)

"""
----------------------- Model for Classifier --------------------------------------
The class SDG - VC - IND that are used to strcture the knowledge repository - for seed and for user
- SDG: Model that includes all 17 SDGs from the UN are presented in the class SDG
- Value_chain: Model for the VC which the use of a Modified Preorder Tree Traversal to classify the different possible Value Chains since they are based on
a hierarchical tree => for parent, specify self since it's hierarchical 
- Industry: Model to include specific industries

For all the self.title is specified to return the title when the object is called
------------------------------------------------------------------------------------
"""
class SDG(models.Model):
    title = models.CharField(max_length=50, unique=True)
    contenu = models.TextField(default="NA")
    image = models.ImageField(upload_to='sdgs/')

    def __str__(self):
        return '{} - {}'.format(self.title, self.contenu)


class Value_chain(MPTTModel):
    parent = TreeForeignKey('self',related_name='children',null=True,blank=True,on_delete=models.CASCADE,default=1)
    title = models.CharField(max_length=50, unique=True)
    contenu = models.TextField(default="NA")

    def __str__(self):
        return self.title


class Industry(models.Model):
    title = models.CharField(max_length=50, unique=True)
    contenu = models.TextField(default="NA")

    def __str__(self):
        return self.title


"""
----------------------- Models for Seed --------------------------------------
The class Seed and it's related models:
- Seed: Model used to represent knowledge from the user on the platform - to classify a specific seed, the classes SDG - VC - IND 
are used. The title of each Seed has to be unique and it's directly connected to its slug !important! to access each seed in the code
- Document_Seed: Model to represent the documents related for each side, one (seed) to many (doc) relationship.
- SDG / VC / IND _ Seed: Models used to represent the connect between each seed and each of the classifier (SDG - VC - IND), each seed
can have many classifier and each classifier can have many seed => manytomany relationship. No return since the databases only have ID (int)
- Comment_Seed: Model to represent the comments associated with each seed. Use of a Modified Preorder Tree Traversal since you can answer
to a comment thread => for parent, specify self since it's hierarchical 
------------------------------------------------------------------------------

"""

class Seed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, default=1)
    profile_seed = models.ImageField(upload_to=profile_seed_directory_path,default="Null")
    title = models.CharField(max_length=100, unique=True,)
    summary = models.TextField(max_length=100,default="NA")
    sdg = models.ManyToManyField(SDG, through="SDG_Seed")
    value_chain = models.ManyToManyField(Value_chain, through="Value_Chain_Seed")
    industry = models.ManyToManyField(Industry, through="Industry_Seed")
    pros = models.TextField(default="NA")
    cons = models.TextField(default="NA")
    contenu = models.TextField(default="NA")
    use_case = models.TextField(default="NA")
    aim_seed = models.CharField(max_length=30, choices=Aims)
    keywords = TaggableManager()
    slug = models.SlugField(max_length = 250, unique=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_publication']

    # connect the slug to the title
    def save(self, *args, **kwargs):                                  # add this
        self.slug = slugify(self.title, allow_unicode=True)           # add this
        super().save(*args, **kwargs)                                 # add this

    def __str__(self):
        return self.title


class Document_Seed(models.Model):
    seed_related = models.ForeignKey(Seed,on_delete=models.CASCADE,default=1)
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=user_directory_path,default="Null")
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description
        

class SDG_Seed(models.Model):
    sdg = models.ForeignKey(SDG, on_delete=models.CASCADE)
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)


class Value_Chain_Seed(models.Model):
    value_chain = models.ForeignKey(Value_chain, on_delete=models.CASCADE)
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)


class Industry_Seed(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE)
    seed = models.ForeignKey(Seed, on_delete=models.CASCADE)


class Comment_Seed(MPTTModel):
    seed_connected = models.ForeignKey(Seed, related_name='comments', on_delete=models.CASCADE)
    parent = TreeForeignKey('self',related_name='children',null=True,blank=True,on_delete=models.CASCADE,default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,default=1)
    content = models.TextField(default="NA")
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['date_posted']
    

    def __str__(self):
        return 'Comment {} by {}'.format(self.content, self.user)


"""
----------------------- Model for Interactions --------------------------------------
The class FS - LS - LC and DS - DS that are used to structure the interactions on the platform specific to seed
- FS: Model that show which users added which seed to its fav
- LS: Model that show which users likes which seed 
- LC: Model that show which users likes which comment
- DS: Model that show which users dislikes which comment
- DC: Model that show which users dislikes which comment

"""
class Favourites_Seed(models.Model):
    seed_related = models.ForeignKey(Seed,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Liked_Seed(models.Model):
    seed_related = models.ForeignKey(Seed,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Liked_Comment(models.Model):
    comment_related = models.ForeignKey(Comment_Seed,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Disliked_Seed(models.Model):
    seed_related = models.ForeignKey(Seed,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Disliked_Comment(models.Model):
    comment_related = models.ForeignKey(Comment_Seed,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


"""
----------------------- Models for Vision --------------------------------------
The class Vision and it's related models:
- Vision: Model used to represent quick thought from the user on the platform
- Comment_Vision: Model to represent the comments associated with each vision. Use of a Modified Preorder Tree Traversal since you can answer
to a comment thread => for parent, specify self since it's hierarchical 

"""

class Vision(models.Model):
    title = models.CharField(max_length=100, unique=True, )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, default=1)
    content = models.TextField(max_length=444,default="NA")
    aim_vision = models.CharField(max_length=30, choices=Aims)
    keywords = TaggableManager()
    slug = models.SlugField(max_length= 250,unique=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):                                  # add this
        self.slug = slugify(self.title, allow_unicode=True)           # add this
        super().save(*args, **kwargs)                                 # add this

    def __str__(self):
        return self.title


class Comment_Vision(MPTTModel):
    vision_connected = models.ForeignKey(Vision, related_name='comments', on_delete=models.CASCADE)
    parent = TreeForeignKey('self',related_name='children',null=True,blank=True,on_delete=models.CASCADE,default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,default=1)
    content = models.TextField(default="NA")
    likes_comment_vision = models.ManyToManyField(User, related_name="likes_comment_vision",default=None,blank=True)
    dislikes_comment_vision = models.ManyToManyField(User, related_name="dislikes_comment_vision",default=None,blank=True)
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['date_posted']
    

    def __str__(self):
        return 'Comment {} by {}'.format(self.content, self.user)


"""
----------------------- Model for Interactions --------------------------------------
The class LV is used to structure the interactions on the platform specific to vision
- LS: Model that show which users likes which vision 
- DS: Model that show which users dislikes which vision 
"""

class Liked_Vision(models.Model):
    vision_related = models.ForeignKey(Vision,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)


class Disliked_Vision(models.Model):
    vision_related = models.ForeignKey(Vision,on_delete=models.CASCADE,default=1)
    user_related = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(default=timezone.now)