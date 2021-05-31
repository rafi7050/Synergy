from django import forms
from django.contrib.auth.models import User
from .models import User, Profile, Feedback, Capabilities, Country
from knowledge.models import SDG, Industry, Value_chain
from mptt.forms import TreeNodeChoiceField
 

# Form to create an user
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email')


# Form to create and edit a profile =>  SDG - CAP - IND - VC - Country are limited choices based on a manytomany relationship
class ProfileForm(forms.ModelForm):
    sdg = forms.ModelMultipleChoiceField(
        queryset=SDG.objects.all().exclude(id=18),
        widget=forms.CheckboxSelectMultiple,
        
        )

    industry = forms.ModelMultipleChoiceField(
        queryset=Industry.objects.all().exclude(id=10),
        widget=forms.CheckboxSelectMultiple,
        )
    
    capabilities = forms.ModelMultipleChoiceField(
        queryset=Capabilities.objects.all().exclude(id=11),
        widget=forms.CheckboxSelectMultiple,
        )
    
    country = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all().exclude(id=237),
        widget=forms.CheckboxSelectMultiple,
        )
    
    value_chain = forms.ModelMultipleChoiceField(
        queryset=Value_chain.objects.all().exclude(id=9),
        widget=forms.CheckboxSelectMultiple,
        )

    class Meta:
        model = Profile
        fields = ('company_name','website','position_of_user','value_chain','country','description','type_user','industry','sdg', 'capabilities','profile_picture')


# Form to delete a user !important! keep fields = empty list
class UserDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []   #Form has only submit button.  Empty "fields" list still necessary, though.
    

# Form to provide a feedback from an user to another
class UserFeedback(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content',]


# Form to search a profile based on SDG - IND - VC - CAP - Country
class SearchProfile(forms.Form):
    sdg_info = forms.ModelMultipleChoiceField(queryset=SDG.objects.all())
    
    value_chain_info = TreeNodeChoiceField(queryset=Value_chain.objects.all(),level_indicator='+--')
    
    industry_info = forms.ModelMultipleChoiceField(queryset=Industry.objects.all())

    capabilities_info =  forms.ModelMultipleChoiceField(queryset=Capabilities.objects.all())

    countries_info =  forms.ModelMultipleChoiceField(queryset=Country.objects.all())

    class Meta:
        model = Profile
        fields = ["sdg_info", "value_chain_info", "industry_info", "capabilities_info", "countries_info"]


# Form to search a profile on its username
class SearchUsername(forms.Form):
    username = forms.CharField()

    class Meta:
        fields = ["username"]




