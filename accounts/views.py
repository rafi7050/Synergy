from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from notifications.signals import notify

from .forms import UserForm, ProfileForm, UserDeleteForm, SearchProfile, UserFeedback, SearchUsername
from .models import Profile, Value_Chain_User, Industry_User, SDG_User, Capabilities_User, Capabilities, Follower, Feedback, Liked_Feedback, Disliked_Feedback, Country_User, Country
from knowledge.models import Seed, Industry, Value_chain, SDG, Comment_Seed, SDG_Seed, Vision, Comment_Vision, Favourites_Seed, Liked_Seed, Disliked_Seed, Liked_Vision, Disliked_Vision

"""
----------------------- Functions for Profile --------------------------------------
- Create of a new user: user_register
- Allow user to logout: logout_request
- Allow user to login: login_request
- View a specific profile: user_profile
- Edit a specific profile: edit_profile
- Edit the password: edit_password
- Delete the profile: delete_user
- Search a profile based on the three classifier and capabilities and country: search_profile
- Results of the search: return_profile
- Search a profile based on the username: search_profile
-------------------------------------------------------------------------------------------
""" 

def user_register(request):
    """
    Aim - Create of a new user
    Description 
    - Retrieve the forms used to create a new user (UserCreationForm) => provided in django.contrib.auth.forms
    - Return to same template to have the error !important!
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username, password=password)
            group = Group.objects.get(name='Stroller') 
            group.user_set.add(user)
            user.save()
            login(request, user)
            messages.success(request, "New account successfully created" )
            return redirect('dashboard:view_dashboard')

        else:
            return render(request,'dist/sign-up.html',{'form':form})

    else:
        form = UserCreationForm()
        return render(request,'dist/sign-up.html',{'form':form})


@login_required
def logout_request(request):
    """
    Aim - Allow user to logout
    Description 
    - Function logout that is provided in django.contrib.auth 
    - Add a message to show to the user
    """
    logout(request)   
    messages.success(request, 'You successfully loged ou')
    return redirect("/")


def login_request(request):
    """
    Aim - Allow user to login
    Description 
    - Retrieve the form used to login (AuthenticationForm) provided in django.contrib.auth.forms
    - Get username and passowrd
    - Function to authenticate user provided in django.contrib.auth
    - Add a message to show to the user

    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  
                messages.success(request, 'You successfully arrived on the platform')
                return redirect('dashboard:view_dashboard')
            else:
                return redirect('home')

        else:
            return redirect('accounts:login')

    form = AuthenticationForm()
    return render(request,'dist/sign-in.html',{'form':form})


@login_required
def user_profile(request,username):
    """
    Aim - View a specific Profile

    Description
    - Retrieve all the objects connected to the wanted profile (sdg / vc / ind / capabilities / country)
    - Verify the flags for follower (y/n) - if request.user is author of profile (y/n)
    - Create a list for the feedback, this allows to include information about current user (already liked feedback?)
    - Post section for a user to add a feedback to the profile
    
    """
    
    # If no such user exists raise 404
    try:
        user = User.objects.get(username=username)
    except:
        return render(request, "dist/inside/profile/404_no_user.html")

    user_profile = User.objects.get(username=username)
    profile_user = Profile.objects.get(user_id=user_profile.id)

    # Industry design
    industry_user = Industry_User.objects.filter(user_id_id=profile_user.id)
    industry = Industry.objects.filter(id__in=[i.industry_id for i in industry_user])

    # VC design
    value_chain_user = Value_Chain_User.objects.filter(user_id=profile_user.id)
    value_chain = Value_chain.objects.filter(id__in=[v.value_chain_id for v in value_chain_user])

    # SDG design
    sdg_user = SDG_User.objects.filter(user_id=profile_user.id)
    sdg = SDG.objects.filter(id__in=[s.sdg_id for s in sdg_user])

    # Capabilities design
    capabilities_user = Capabilities_User.objects.filter(user_id_id=profile_user.id)
    capabilities = Capabilities.objects.filter(id__in=[ca.capabilities_id for ca in capabilities_user])
   
    # Country design
    country_user = Country_User.objects.filter(user_id_id=profile_user.id)
    country = Country.objects.filter(id__in=[cu.country_id for cu in country_user])

    # List for the feedback
    feedback_list = []
    feedback_user = Feedback.objects.filter(to_user_id=profile_user.id)
    for feedback in feedback_user:
        my_dict = {'Feedback': [],'Liked': [], 'Disliked': [], 'From_User': [], 'Content': [], 'L_count': [], 'D_count': []}
        my_dict['Feedback'].append(feedback.id)
        my_dict['From_User'].append(feedback.from_user)
        my_dict['Content'].append(feedback.content)

        # Verify if liked already
        if Liked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).exists():
            my_dict['Liked'].append(True)
        else:
            my_dict['Liked'].append(False)

        # Verify if disliked already
        if Disliked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).exists():
            my_dict['Disliked'].append(True)
        else:
            my_dict['Disliked'].append(False)
        
        # Count the likes
        feedback_likes = Liked_Feedback.objects.filter(feedback_related_id=feedback.id).count
        my_dict['L_count'].append(feedback_likes)

        # Count the dislikes
        feedback_dislikes = Disliked_Feedback.objects.filter(feedback_related_id=feedback.id).count
        my_dict['D_count'].append(feedback_dislikes)
        
        feedback_list.append(my_dict)

    # Flag for Followers 
    follower_count = Follower.objects.filter(user_to_id=user_profile.id).count
    following_count = Follower.objects.filter(user_from_id=user_profile.id).count

    follower = False
    if Follower.objects.filter(Q(user_from_id=request.user.id) & Q(user_to_id=user_profile.id)).exists():
        follower = True

    # Flag that determines if we are the user
    editable = False
    if request.user == user:
        editable = True

    # Post a feedback on the user
    if request.method == "POST":
        form_feedback = UserFeedback(request.POST)
        if form_feedback.is_valid():
            feedback_on_user = form_feedback.save(commit=False)
            feedback_on_user.from_user = request.user
            feedback_on_user.to_user = user_profile
            feedback_on_user.save()
            return redirect(reverse(("accounts:user_profile"),args=[user_profile.username]))

    else:
        form_feedback = UserFeedback(request.POST)

    context = {
        "user_profile": user_profile, 
        "profile_user": profile_user,
        "capabilities":capabilities,
        "capabilities_user": capabilities_user, 
        "feedback_user": feedback_user,
        "feedback_list": feedback_list,
        "editable": editable,
        "industry": industry,
        "value_chain_user": value_chain_user,
        "value_chain": value_chain,
        "country": country,
        "country_user": country_user,
        "sdg_user": sdg_user,
        "sdg": sdg,
        "form_feedback": form_feedback,
        "follower": follower,
        "follower_count": follower_count,
        "following_count": following_count,
    }

    return render(request, "dist/inside/profile/profile.html", context)


@login_required
@transaction.atomic
def edit_profile(request):
    """
    Aim - Edit a specific profile
    Description
    - Get the user and profile that need that want to be edited using the request.user
    - Retrieve the two forms used to create a profile (UserForm - ProfileForm) => 
      instance = request.user
    - Save the two forms
    - Return to the newly edited profile using the request.user.username 
    - Add a message to show to the user (In case of error => an error is raised in the form)

    """

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save() 
            messages.success(request, 'Your profile was successfully updated!')
            return redirect(reverse(("accounts:user_profile"),args=[request.user.username]))
  
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'dist/inside/profile/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def edit_password(request):
    """
    Aim - Edit the password
    Description
    - Retrieve the form used to login (PasswordChangeForm) provided in django.contrib.auth.forms
    - Save the form
    - Update the session so the new session consider the new passowrd provided in django.contrib.auth
    - Return to the newly edited profile using the request.user.username 
    - Add a message to show to the user (In case of error => an error is raised in the form)

    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(reverse(("accounts:user_profile"),args=[request.user.username]))

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'dist/inside/profile/edit_password.html', {
        'form': form
    })


@login_required
def delete_user(request):
    """
    Aim - Delete the profile
    Description
    - Retrieve the form used to delete (UserDeleteForm) provided in django.contrib.auth.forms
    - Assign to the request user
    - Delete user
    - Add a message to show to the user

    """
    if request.method == 'POST':
        delete_form = UserDeleteForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect("/")
    else:
        delete_form = UserDeleteForm(instance=request.user)

    return render(request,'dist/inside/profile/delete_user.html', context={'delete_form': delete_form})


@login_required
def search_profile(request):
    """
    Aim - Search a profile based on the three classifier and capabilities and country
    Description
    - Get the form to search a profile
    - In template the action is going to send the results to return_profile (next function)
    """
 
    user_profile = SearchProfile(request.GET)
    return render(request, "dist/inside/profile/search_profile.html", context={"user_profile":user_profile})


@login_required
def return_profile(request):
    """
    Aim - Results of the search
    Description
    - Get the form to search a profile from the search_profile (previous function)
    - Verify is for is valid 
    - Retrieve all the objects connected to the wanted seed (sdg_info + value_chain_info + industry_info + capabilities_info + country_info)
    - Retrieve all the objects for the design _front = want to have the name of the related classifier since the previous DB only ID
    - Retrieve the required seed from the databased using the if - elif statement. True = all of the classifier

    """
    if request.method == 'GET':
        form = SearchProfile(request.GET)

        if form.is_valid():
            sdg_info = request.GET.get('sdg_info')
            value_chain_info = request.GET.get('value_chain_info')
            industry_info = request.GET.get('industry_info')
            capabilities_info = request.GET.get('capabilities_info')
            country_info = request.GET.get('countries_info')
            sdg_search = SDG.objects.filter(id=sdg_info)
            vc_search = Value_chain.objects.filter(id=value_chain_info)
            ind_search = Industry.objects.filter(id=industry_info)
            cap = Capabilities.objects.filter(id=capabilities_info)
            coun = Country.objects.filter(id=country_info)

            try:
                # all true
                if sdg_info == "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info == "11" and country_info == "237":
                    profile_view = Profile.objects.all() 
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities
                elif sdg_info == "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    profile_view = Profile.objects.filter(id__in=[cap.user_id_id for cap in capabilities_profile])
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except sdg
                elif sdg_info != "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info == "11" and country_info == "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    profile_view = Profile.objects.filter(Q(id__in=[sdg.user_id_id for sdg in sdg_related]))
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except vc
                elif sdg_info == "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info == "11" and country_info == "237":
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(id__in=[vc.user_id_id for vc in value_chain_related])
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ]) 
                
                # all true except int
                elif sdg_info == "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info == "11" and country_info == "237":
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(id__in=[ind.user_id_id for ind in industry_related])
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except country
                elif sdg_info == "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info == "11" and country_info != "237":
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(id__in=[ind.user_id_id for ind in country_related])
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities and sdg
                elif sdg_info != "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities and vc
                elif sdg_info == "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
            
                # all true except capabilities and country
                elif sdg_info == "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[country.user_id_id for country in country_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and industry
                elif sdg_info == "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except country and industry
                elif sdg_info == "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info == "11" and country_info != "237":
                    country_related = Country_User.objects.filter(country_id=country_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except sdg and vc
                elif sdg_info != "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info == "11" and country_info == "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except sdg and country
                elif sdg_info != "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info == "11" and country_info != "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[country.user_id_id for country in country_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except sdg and industry
                elif sdg_info != "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info == "11" and country_info == "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except vc and ind
                elif sdg_info == "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info == "11" and country_info == "237":
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except vc and country
                elif sdg_info == "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info == "11" and country_info != "237":
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[country.user_id_id for country in country_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except sdg and vc and industry
                elif sdg_info != "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info == "11" and country_info == "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except country and vc and industry
                elif sdg_info == "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info == "11" and country_info != "237":
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except sdg and vc and country
                elif sdg_info != "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info == "11" and country_info != "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[country.user_id_id for country in country_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except sdg and country and industry
                elif sdg_info != "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info == "11" and country_info != "237":
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities and sdg and industry 
                elif sdg_info != "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities and sdg and country 
                elif sdg_info != "18" and value_chain_info == "1" and industry_info == "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[country.user_id_id for country in country_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and country and industry 
                elif sdg_info == "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and sdg and vc 
                elif sdg_info != "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and country and vc 
                elif sdg_info == "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except capabilities and industry and vc 
                elif sdg_info == "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[industry.user_id_id for industry in industry_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and industry and vc and sdg
                elif sdg_info != "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info != "11" and country_info == "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])
                
                # all true except capabilities and industry and vc and country
                elif sdg_info == "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except sdg and industry and vc and country
                elif sdg_info != "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info == "11" and country_info != "237":
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except sdg and industry and capabilities and country
                elif sdg_info != "18" and value_chain_info == "1" and industry_info != "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all true except sdg and value_chain and capabilities and country
                elif sdg_info != "18" and value_chain_info != "1" and industry_info == "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

                # all wrong
                elif sdg_info != "18" and value_chain_info != "1" and industry_info != "10" and capabilities_info != "11" and country_info != "237":
                    capabilities_profile = Capabilities_User.objects.filter(capabilities_id=capabilities_info)
                    industry_related = Industry_User.objects.filter(industry_id=industry_info)
                    sdg_related = SDG_User.objects.filter(sdg_id=sdg_info)
                    country_related = Country_User.objects.filter(country_id=country_info)
                    value_chain_related = Value_Chain_User.objects.filter(value_chain_id=value_chain_info)
                    profile_view = Profile.objects.filter(
                        Q(id__in=[country.user_id_id for country in country_related]) & Q(id__in=[cap.user_id_id for cap in capabilities_profile]) & Q(id__in=[sdg.user_id_id for sdg in sdg_related]) & Q(id__in=[value_chain.user_id_id for value_chain in value_chain_related]) & Q(id__in=[industry.user_id_id for industry in industry_related])
                        )
                    user_list = User.objects.filter(id__in=[pro.id for pro in profile_view ])

            except:
                profile_view = None
                user_list = None

        else:
            form = SearchProfile(request.GET)

        return render(request, "dist/inside/profile/return_profile.html",
        context={
            "sdg_info": int(sdg_info),
            "industry_info": int(industry_info),
            "capabilities_info": int(capabilities_info),
            "value_chain_info": int(value_chain_info),
            "country_info": int(country_info),
            "sdg_search": sdg_search,
            "vc_search": vc_search,
            "ind_search": ind_search,
            "cap": cap,
            "coun": coun,
            "profile_view":profile_view,
            "user_list": user_list,})


@login_required
def search_username(request):
    """
    Aim - Search a profile based on the username
    Description
    - Get the form to search a profile for the username
    - The action is kept on the same page
        .Try : find a profile with the username
        .Except : return no profile
    """
    form_username = SearchUsername(request.GET)
    # Provide the search query
    if request.method == 'GET':
        form_username = SearchUsername(request.GET)
        if form_username.is_valid():
            username = request.GET.get('username')
            try:
                if User.objects.filter(username__icontains=username).exists():
                    found = "yes"
                    uview = User.objects.filter(username__icontains=username)
                    pview = Profile.objects.filter(id__in=[pv.id for pv in uview])
                else:
                    found = "no"
                    uview = User.objects.all()
                    pview = Profile.objects.all()

            except:
                found = "no"
                uview = User.objects.all()
                pview = Profile.objects.all()

        else:
            form_username = SearchUsername(request.GET)
            found = "okay"
            uview = User.objects.all()
            pview = Profile.objects.all()

    else:
        form_username = SearchUsername(request.GET)
        found = "okay"
        uview = User.objects.all()
        pview = Profile.objects.all()

    return render(request, "dist/inside/profile/search_username.html", context = {'found': found,'uview': uview, 'pview': pview, 'form_username': form_username})

"""
----------------------- Functions for Activities --------------------------------------
- Add a seed to favourites : seed_add_fav
- Like a seed: seed_add_like
- Dislike a seed: seed_add_dislike
- Follow another profile - user: profile_follow_user
- View the followers the user is following: view_followed
- View the followers that are following the user: view_follower
- Like a feedback on a profile: profile_like_feedback
- Dislike a feedback on a profile: profile_dislike_feedback
- View the user' favourites: view_fav
- View the seeds created by the user: view_seed_created 
- View the vision created by the user: view_vision_created 
- View the user' liked seed and vision: view_like
- View the user' dislikes: view_dislike
- Like a vision: vision_add_like
- Dislike a vision: vision_add_dislike
-------------------------------------------------------------------------------------------
""" 


@login_required
def seed_add_fav(request, slug):
    """
    Aim - Add a seed to favourites 
    Description
    - Get the seed that need to be added using the slug that in provided in the button from the template
    - If already part of favourites remove it
    - Else add it
    - Return HTTP_REFERER to reload the page once the action is terminated
    - Add a message to show to the user

    """
    seed_fav = Seed.objects.get(slug=slug)
    if Favourites_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_fav.id)).exists():
        Favourites_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_fav.id)).delete()
        messages.success(request, 'It was deleted from your favourites')
    else:
        favourites = Favourites_Seed(user_related=request.user)
        favourites.seed_related = seed_fav
        favourites.save()
        messages.success(request, 'It was added to your favourites')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def seed_add_like(request, slug):
    """
    Aim - Like a seed
    Description
    - Get the seed that need to be liked using the slug that in provided in the button from the template
    - If already liked remove the like of the seed
    - Else add the like of the seed
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    seed_l = Seed.objects.get(slug=slug)
    if Liked_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_l.id)).exists():
        Liked_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_l.id)).delete()
    else:
        seed_save = Liked_Seed(user_related=request.user)
        seed_save.seed_related = seed_l
        seed_save.save()
        if request.user != seed_l.user:
            notify.send(request.user, recipient=seed_l.user, verb="like the seed")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def seed_add_dislike(request, slug):
    """
    Aim - Dislike a seed
    Description
    - Get the seed that need to be disliked using the slug that in provided in the button from the template
    - If already disliked remove the dislike of the seed
    - Else add the dislike of the seed
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    seed_d = Seed.objects.get(slug=slug)
    if Disliked_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_d.id)).exists():
        Disliked_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=seed_d.id)).delete()
    else:
        seed_save = Disliked_Seed(user_related=request.user)
        seed_save.seed_related = seed_d
        seed_save.save()
        if request.user != seed_d.user:
            notify.send(request.user, recipient=seed_d.user, verb="Dislike the seed")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def profile_follow_user(request, username):
    """
    Aim - Follow another profile - user
    Description
    - Get the profile that need to be followed using the username that in provided in the button from the template
    - If already followed remove the following of the request.user
    - Else add the following of the request.user
    - Return HTTP_REFERER to reload the page once the action is terminated
    - Add a message to show to the user

    """
    user_followed = User.objects.get(username=username)
    if Follower.objects.filter(Q(user_from_id=request.user.id) & Q(user_to_id=user_followed.id)).exists():
        f = Follower.objects.get(Q(user_from_id=request.user.id) & Q(user_to_id=user_followed.id))
        f.delete()
        messages.success(request, 'It was deleted from your following')
    else:
        f = Follower(user_from_id=request.user.id, user_to_id=user_followed.id)
        f.save()
        messages.success(request, 'It was added to your following')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def view_followed(request, username):
    """
    Aim - View the followers the user is following
    Description
    - Get the profile that we want to have the followed about using the username that in provided in the button from the template
    - Look for all profile that the profile is following in Followed DB
    - Associate the appropriate user and profile to the retrieved profiles

    """
    user_of_profile = User.objects.get(username=username)
    followed = Follower.objects.filter(user_from_id=user_of_profile.id)
    user_followed = User.objects.filter(id__in=[foll.user_to_id for foll in followed])
    profile_followed = Profile.objects.filter(id__in=[foll.user_to_id for foll in followed])

    return render(request, "dist/inside/profile/view_followed.html", context={"user_of_profile": user_of_profile, "user_followed":user_followed, "profile_followed":profile_followed})


@login_required
def view_follower(request, username):
    """
    Aim - View the followers that are following the user 
    Description
    - Get the profile that we want to have the followed about using the username that in provided in the button from the template
    - Look for all profile that the profile is following in Followed DB
    - Associate the appropriate user and profile to the retrieved profiles

    """
    user_of_profile = User.objects.get(username=username)
    followed = Follower.objects.filter(user_to_id=user_of_profile.id)
    user_followed = User.objects.filter(id__in=[foll.user_from_id for foll in followed])
    profile_followed = Profile.objects.filter(id__in=[foll.user_from_id for foll in followed])

    return render(request, "dist/inside/profile/view_follower.html", context={"user_of_profile": user_of_profile, "user_followed":user_followed, "profile_followed":profile_followed})
from . import views
from notifications.signals import notify
@login_required
def profile_like_feedback(request, pk):
    """
    Aim - Like a feedback on a profile
    Description
    - Get the feedback that need to be liked using the pk that in provided in the button from the template
    - If already liked remove the like of the feedback
    - Else add the like of the feedback
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    feedback = Feedback.objects.get(id=pk)
    if Liked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).exists():
        Liked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).delete()
    else:
        feedback_pro = Liked_Feedback(user_related=request.user)
        feedback_pro.feedback_related = feedback
        feedback_pro.save()
        if request.user != feedback.user:
            notify.send(request.user, recipient=feedback.user, verd="has liked your feedback")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def profile_dislike_feedback(request, pk):
    """
    Aim - Dislike a feedback on a profile
    Description
    - Get the feedback that need to be disliked using the pk that in provided in the button from the template
    - If already disliked remove the dislikeof the feedback
    - Else add the dislike of the feedback
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    feedback = Feedback.objects.get(id=pk)
    if Disliked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).exists():
        Disliked_Feedback.objects.filter(Q(user_related_id=request.user.id) & Q(feedback_related_id=feedback.id)).delete()
    else:
        feedback_pro = Disliked_Feedback(user_related=request.user)
        feedback_pro.feedback_related = feedback
        feedback_pro.save()
        if request.user != feedback.user:
            notify.send(request.user, recipient=feedback.user, verd="has disliked your feedback")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def view_fav(request,username):
    """
    Aim - View the user' favourites 
    Description
    - Get the user and the related seed

    """
    user_profile = User.objects.get(username=username)
    fav_seed = Favourites_Seed.objects.filter(user_related_id=user_profile.id)
    seed = Seed.objects.filter(id__in=[fv.seed_related_id for fv in fav_seed])
    author = User.objects.filter(id__in=[a.user_id for a in seed])
    return render(request, "dist/inside/profile/favourites.html", context={"seed":seed, "user_profile": user_profile, "author": author})


@login_required
def view_seed_created(request,username):
    """
    Aim - View the seed created by the user
    Description
    - Get the user and the related seed

    """
    user_profile = User.objects.get(username=username)
    seed = Seed.objects.filter(user_id=user_profile.id)
    return render(request, "dist/inside/profile/seed_created.html", context={"seed":seed, "user_profile": user_profile})


@login_required
def view_vision_created(request,username):
    """
    Aim - View the user' favourites 
    Description
    - Get the user and the related seed

    """
    user_profile = User.objects.get(username=username)
    vision_created = Vision.objects.filter(user_id=user_profile.id)

    # Flag to see if request user is viewing is one likes
    editable = False
    if request.user == user_profile:
        editable = True


    aim = {
        1: "To raise awarness",
        2: "To share a product or service",
        3: "To search for improvement",
        4: "To present theoretical results ",
        5: "To make laugh",
        6: "Others",
        }
    
    list = []

    for vision in vision_created:
        my_dict = {'Type': [], 'ID': [], 'Name': [] , 'Date': [], 'Slug': [], 'Content': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
        my_dict['Type'].append("Vision")
        my_dict['Name'].append(vision.title)
        my_dict['ID'].append(vision.id)
        my_dict['Date'].append(vision.date_publication)
        my_dict['Slug'].append(vision.slug)
        my_dict['Content'].append(vision.content)
        my_dict['Description'].append(vision.keywords)
        # Find the real title of the aim
        for keys in aim:
            if int(vision.aim_vision) == keys:
                my_dict['Aim'].append(aim[keys])

        #Counts the likes
        vision_likes = Liked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Likes'].append(vision_likes)

        #Counts the dislikes
        vision_dislikes = Disliked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Dislikes'].append(vision_dislikes)

        # Look if the comment was already liked or not 
        if Liked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        if Disliked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")
                        
        list.append(my_dict)

    return render(request, "dist/inside/profile/vision_created.html", context={"list":list, "user_profile": user_profile, "vision_created": vision_created, "editable": editable})


@login_required
def view_like(request,username):
    """
    Aim - VView the user' liked seed and vision
    Description
    - Get the user and the related seed / vision
    - See if the user is the owner of the likes
    - Add the related seed and vision to a list in order to process both in the template

    """
    user_profile = User.objects.get(username=username)
    #seed
    seed_liked_view = Liked_Seed.objects.filter(user_related_id=user_profile.id)
    seed_interest = Seed.objects.filter(id__in=[slv.seed_related_id for slv in seed_liked_view])
    profile_seed_interest = User.objects.filter(id__in=[psi.user_id for psi in seed_interest])
    #vision
    vision_liked_view = Liked_Vision.objects.filter(user_related_id=user_profile.id)
    vision_following = Vision.objects.filter(id__in=[vlv.vision_related_id for vlv in vision_liked_view])
    profile_vision_interest = User.objects.filter(id__in=[pvi.user_id for pvi in vision_following])

    # Flag to see if request user is viewing is one likes
    editable = False
    if request.user == user_profile:
        editable = True

    aim = {
        1: "To raise awarness",
        2: "To share a product or service",
        3: "To search for improvement",
        4: "To present theoretical results ",
        5: "To make laugh",
        6: "Others",
        }
    list = []
    x = 0

    for seed in seed_interest:
        my_dict = {'Type': [],'ID': [],'NBR': [],'Name': [], 'Author': [], 'Date': [], 'Slug': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [],}
        my_dict['Type'].append("Seed")
        my_dict['NBR'].append(x)
        my_dict['Name'].append(seed.title)
        my_dict['ID'].append(seed.id)
        my_dict['Date'].append(seed.date_publication)
        my_dict['Slug'].append(seed.slug)
        my_dict['Description'].append(seed.summary)
        # Find the author
        for user in profile_seed_interest:
            if user.id == seed.user_id:
                my_dict['Author'].append(user.username)

        # Find the real title of the aim
        for keys in aim:
            if int(seed.aim_seed) == keys:
                my_dict['Aim'].append(aim[keys])

        #Counts the likes
        seed_likes = Liked_Seed.objects.filter(seed_related_id=seed.id).count
        my_dict['Likes'].append(seed_likes)

        #Counts the dislikes
        seed_dislikes = Disliked_Seed.objects.filter(seed_related_id=seed.id).count
        my_dict['Dislikes'].append(seed_dislikes)
        
        x += 1
        list.append(my_dict)

    for vision in vision_following:
        my_dict = {'Type': [], 'ID': [],'NBR': [], 'Author': [], 'Name': [] , 'Date': [], 'Slug': [], 'Content': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
        my_dict['Type'].append("Vision")
        my_dict['NBR'].append(x)
        my_dict['Name'].append(vision.title)
        my_dict['ID'].append(vision.id)
        my_dict['Date'].append(vision.date_publication)
        my_dict['Slug'].append(vision.slug)
        my_dict['Content'].append(vision.content)
        my_dict['Description'].append(vision.keywords)
        # Find the author of the vision
        for user in profile_vision_interest:
            if user.id == vision.user_id:
                my_dict['Author'].append(user.username)

        # Find the real title of the aim
        for keys in aim:
            if int(vision.aim_vision) == keys:
                my_dict['Aim'].append(aim[keys])

        #Counts the likes
        vision_likes = Liked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Likes'].append(vision_likes)

        #Counts the dislikes
        vision_dislikes = Disliked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Dislikes'].append(vision_dislikes)

        # Look if the comment was already liked or not 
        if Liked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        
        if Disliked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")
                        

        x += 1
        list.append(my_dict)

    return render(request, "dist/inside/profile/likes.html", context={"list":list,"user_profile":user_profile, "editable": editable, "seed_interest": seed_interest, "vision_following": vision_following })


@login_required
def view_dislike(request,username):
    """
    Aim - View the user' likes
    Description
    - Get the user and the related seed / vision
    - See if the user is the owner of the likes
    - Add the related seed and vision to a list in order to process both in the template

    """
    user_profile = User.objects.get(username=username)
    seed_disliked_view = Disliked_Seed.objects.filter(user_related_id=user_profile.id)
    seed_interest = Seed.objects.filter(id__in=[slv.seed_related_id for slv in seed_disliked_view])
    vision_disliked_view = Disliked_Vision.objects.filter(user_related_id=user_profile.id)
    vision_following = Vision.objects.filter(id__in=[vlv.vision_related_id for vlv in vision_disliked_view])

    # Flag to see if request user is viewing is one likes
    editable = False
    if request.user == user_profile:
        editable = True


    aim = {
        1: "To raise awarness",
        2: "To share a product or service",
        3: "To search for improvement",
        4: "To present theoretical results ",
        5: "To make laugh",
        6: "Others",
        }
    list = []
    x = 0

    for seed in seed_interest:
        my_dict = {'Type': [],'NBR': [],'Name': [] , 'Date': [], 'Slug': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [],}
        my_dict['Type'].append("Seed")
        my_dict['NBR'].append(x)
        my_dict['Name'].append(seed.title)
        my_dict['Date'].append(seed.date_publication)
        my_dict['Slug'].append(seed.slug)
        my_dict['Description'].append(seed.description)
        # Find the real title of the aim
        for keys in aim:
            if int(seed.aim_seed) == keys:
                my_dict['Aim'].append(aim[keys])

        #Counts the likes
        seed_likes = Liked_Seed.objects.filter(seed_related_id=seed.id).count
        my_dict['Likes'].append(seed_likes)

        #Counts the dislikes
        seed_dislikes = Disliked_Seed.objects.filter(seed_related_id=seed.id).count
        my_dict['Dislikes'].append(seed_dislikes)
        
        x += 1
        list.append(my_dict)

    for vision in vision_following:
        my_dict = {'Type': [],'NBR': [],'Name': [] , 'Date': [], 'Slug': [], 'Content': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
        my_dict['Type'].append("Vision")
        my_dict['NBR'].append(x)
        my_dict['Name'].append(vision.title)
        my_dict['Date'].append(vision.date_publication)
        my_dict['Slug'].append(vision.slug)
        my_dict['Content'].append(vision.content)
        my_dict['Description'].append(vision.keywords)
        # Find the real title of the aim
        for keys in aim:
            if int(vision.aim_vision) == keys:
                my_dict['Aim'].append(aim[keys])

        #Counts the likes
        vision_likes = Liked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Likes'].append(vision_likes)

        #Counts the dislikes
        vision_dislikes = Disliked_Vision.objects.filter(vision_related_id=vision.id).count
        my_dict['Dislikes'].append(vision_dislikes)


        # Look if the comment was already liked or not 
        if Liked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        
        if Disliked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")
                        

        x += 1
        list.append(my_dict)

    return render(request, "dist/inside/profile/likes.html", context={"list":list,"user_profile":user_profile, "editable": editable,})


@login_required
def vision_add_like(request, slug):
    """
    Aim - Like a vision
    Description
    - Get the vision that need to be liked using the slug that in provided in the button from the template
    - If already liked remove the like 
    - Else add the like
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    vision = Vision.objects.get(slug=slug)
    if Liked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
        Liked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).delete()
    else:
        vision_save = Liked_Vision(user_related=request.user)
        vision_save.vision_related = vision
        vision_save.save()
        if request.user != vision.user:
            notify.send(request.user, recipient=vision.user, verb="Like the vision")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def vision_add_dislike(request, slug):
    """
    Aim - Dislike a vision
    Description
    - Get the vision that need to be disliked using the slug that in provided in the button from the template
    - If already disliked remove the dislike 
    - Else add the dislike 
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    vision = Vision.objects.get(slug=slug)
    if Disliked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).exists():
        Disliked_Vision.objects.filter(Q(user_related_id=request.user.id) & Q(vision_related_id=vision.id)).delete()
    else:
        vision_save = Disliked_Vision(user_related=request.user)
        vision_save.vision_related = vision
        vision_save.save()
        if request.user != vision.user:
            notify.send(request.user, recipient=vision.user, verb="Dislike the vision")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

from django.shortcuts import render

def notification(request):
    return render(request, 'dist/inside/notification.html' )