from django.forms import ModelForm
from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import Seed, Document_Seed, SDG, SDG_Seed, Value_chain, Value_Chain_Seed, Industry, Industry_Seed, Comment_Seed, Vision
from mptt.forms import TreeNodeChoiceField


"""
----------------------- Forms for Seed --------------------------------------
"""
# Form to create a seed, for sdg and industry only selection from the database + exclude all 
class SeedForm(forms.ModelForm):
    sdg = forms.ModelMultipleChoiceField(
        queryset=SDG.objects.all().exclude(id=18),
        widget=forms.CheckboxSelectMultiple,
        )

    industry = forms.ModelMultipleChoiceField(
        queryset=Industry.objects.all().exclude(id=10),
        widget=forms.CheckboxSelectMultiple,
        )
    
    class Meta:
        model = Seed
        fields = ["title", "profile_seed", "sdg", "summary","aim_seed", "keywords", "industry", "pros", "cons", "contenu", "use_case"]


# Form to create to add the VC to a seed, seperate from SeedForm since MPTT wasn't working when include (vc not iterable)
# TreeNodeChoiceField is provided directly from the module mptt
class SeedFormVC(forms.ModelForm):
    value_chain = TreeNodeChoiceField(queryset=Value_chain.objects.all().exclude(id=9))

    class Meta:
        model = Value_Chain_Seed
        fields = ['value_chain']


# Form used to query seed based on their keywords
class SearchKeywords(forms.ModelForm):

    class Meta:
        model = Seed
        fields = ['keywords'] 

# Form to comment on a seed, again using MPTT so having a parent, some specific code in __init__
class CommentFormSeed(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment_Seed.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # parent widget cancelled
        self.fields['parent'].widget.attrs.update({'class': 'd-none'})
        # parent label cancelled
        self.fields['parent'].label = ''
        # need to have a parent avoided
        self.fields['parent'].required = False


    class Meta:
        model = Comment_Seed
        fields = ['content', 'parent']
        

# Form to add a file to the seed, tried to have multiple option but failed when registering a seed
class DocumentFormSeed(forms.ModelForm):
    class Meta:
        model = Document_Seed
        file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
        fields = ['description', 'file']

# Form to delete a seed !important! keep fields = empty list
class SeedDeleteForm(forms.ModelForm):
    class Meta:
        model = Seed
        fields = []   


# Form to search a seed based on SDG - IND - VC
class SearchSeed(forms.Form):
    sdg_info = forms.ModelMultipleChoiceField(
        queryset=SDG.objects.all()
        )
    
    value_chain_info = TreeNodeChoiceField(queryset=Value_chain.objects.all(),level_indicator='+--')
    
    industry_info = forms.ModelMultipleChoiceField(
        queryset=Industry.objects.all()
        )

    class Meta:
        model = Seed
        fields = ["sdg_info", "value_chain_info", "industry_info", ]


"""
----------------------- Form for Vision --------------------------------------
"""

# Form to create a vision
class VisionForm(forms.ModelForm):

    class Meta:
        model = Vision
        fields = ['title', 'content', 'keywords', 'aim_vision']
        