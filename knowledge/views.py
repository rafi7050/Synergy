from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower


from accounts.models import User
from .forms import SeedForm, DocumentFormSeed, SeedFormVC, CommentFormSeed, SeedDeleteForm, SearchSeed, SearchKeywords, VisionForm
from .models import Seed, Document_Seed, SDG_Seed, SDG, Value_chain, Value_Chain_Seed, Industry, Industry_Seed, Comment_Seed, Vision, Favourites_Seed, Liked_Seed, Disliked_Seed, Liked_Comment, Disliked_Comment, Liked_Vision, Disliked_Vision
from taggit.models import Tag

# to define which groups is allowed to perform an action
from .decorations import allowed_users

"""
----------------------- Functions for Seed --------------------------------------
- Create a seed: seed_create
- View a specific seed + comment on seed: one_seed
- Edit a specific seed: seed_edit
- Like a comment on a seed: comment_add_like
- Dislike a comment on a seed: comment_add_dislike
- Delete your comment on a seed: seed_delete_comment
- Add a document on a seed: seed_add_doc
- Delete a document on a seed: seed_delete_doc
- Delete a seed: seed_delete
- Search a seed based on the three classifier: search_seed
- Results of the search: return_seed
- Search a seed based on a keyword: search_keywords_view
----------------------------------------------------------------------------------
"""

@login_required
# only specific users can create a seed 
@allowed_users(allowed_roles=['Staff', 'Gardener'])
def seed_create(request):
    """
    Aim - Create a seed
    Description 
    - Retrieve the three forms used to create a seed (SeedForm - SeedFormVC - DocumentFormSeed)
    - Verify their validity
    - Connect SeedFormVC + DocumentFormSeed to the related seed
    - Save seed - vc - document - m2m (tags pip)
    - Return to the newly created seed using the slug that was just created as the argument
    - Add a message to show to the user
    """

    if request.method == "POST":
        seed_form = SeedForm(request.POST, request.FILES)
        seed_vc = SeedFormVC(request.POST)
        docu_form = DocumentFormSeed(request.POST, request.FILES)
        if seed_form.is_valid() and docu_form.is_valid() and seed_vc.is_valid(): 
            seed_form.instance.user = request.user
            seed = seed_form.save(commit=False)
            seed.save()
            seed_form.save_m2m()
            seed_vc.instance.seed = seed
            seed_vc.save()
            docu_form.instance.seed_related = seed
            docu_form.save()
            messages.success(request, 'Your seed was successfully created!')
            return redirect(reverse(("knowledge:one_seed"),args=[seed.slug]))
        
        else:
            return render(request, "dist/inside/knowledge/seed/create_seed.html", context={"seed_form": seed_form, "docu_form": docu_form, "seed_vc": seed_vc,})
            
    else:
        seed_form = SeedForm(request.POST, request.FILES)
        docu_form = DocumentFormSeed(request.POST, request.FILES)
        seed_vc = SeedFormVC(request.POST)

    return render(request, "dist/inside/knowledge/seed/create_seed.html", context={"seed_form": seed_form, "docu_form": docu_form, "seed_vc": seed_vc,})


@login_required
def one_seed(request, slug):
    """
    Aim - View a specific seed
    Description
    - Retrieve all the objects connected to the wanted seed (sdg / vc / ind / comment / document )
    - Retrieve first sdg to put the image for the strcture
    - Verify the flags for favourites (y/n) - likes (y/n) - dislikes (y/n) - if request.user is author of seed (y/n)
    - Post section for a user to add a comment to the seed
    - Create a list for the comment, this allows to include information about current user (already liked comment?)
    
    """

    one_seed = Seed.objects.get(slug=slug)
    docu_seed = Document_Seed.objects.filter(seed_related=one_seed.id)

    # industry information
    industry_seed = Industry_Seed.objects.filter(seed_id=one_seed.id)
    industry_front = Industry.objects.filter(id__in=[i.industry_id for i in industry_seed])

    # vc information
    value_chain_seed = Value_Chain_Seed.objects.filter(seed_id=one_seed.id)
    value_chain_front = Value_chain.objects.filter(id__in=[v.value_chain_id for v in value_chain_seed])
    
    # sdg information
    sdg_seed = SDG_Seed.objects.filter(seed_id=one_seed.id)
    sdg_front = SDG.objects.filter(id__in=[s.sdg_id for s in sdg_seed])

    # for the image
    sdg_seed_image = SDG_Seed.objects.filter(seed_id=one_seed.id).first()
    
    # Flag to see if already part of favourites
    fav = False
    if Favourites_Seed.objects.filter(Q(user_related_id=request.user.id) & Q(seed_related_id=one_seed.id)).exists():
        fav = True

    # Flag to see like information
    like_count = Liked_Seed.objects.filter(seed_related_id=one_seed.id).count
    like = False
    if Liked_Seed.objects.filter(Q(seed_related_id=one_seed.id) & Q(user_related_id=request.user.id)).exists():
        like = True

    # Flag to see if already part of dislikes
    dislike_count = Disliked_Seed.objects.filter(seed_related_id=one_seed.id).count
    dislike = False
    if Disliked_Seed.objects.filter(Q(seed_related_id=one_seed.id) & Q(user_related_id=request.user.id)).exists():
        dislike = True

    # Flag to see if user can edit
    editable = False
    if request.user == one_seed.user:
        editable = True
    
    # Code to comment on the seed
    if request.method == "POST":
        form_comment = CommentFormSeed(request.POST)
        if form_comment.is_valid():
            comment = form_comment.save(commit=False)
            comment.user = request.user
            comment.seed_connected = one_seed
            comment.save()
            return redirect(reverse('knowledge:one_seed',args=[one_seed.slug]))

    else:
        form_comment = CommentFormSeed(request.POST)


    # List for the feedback
    comment_list = []
    comment_seed = Comment_Seed.objects.filter(seed_connected_id=one_seed.id)
    for comment in comment_seed:
        my_dict = {'ID': [],'Date': [],'Liked': [], 'Disliked': [], 'From_User': [], 'Content': [], 'L_count': [], 'D_count': []}
        my_dict['ID'].append(comment.id)
        my_dict['Date'].append(comment.date_posted)
        my_dict['From_User'].append(comment.user_id)
        my_dict['Content'].append(comment.content)

        # Verify if liked already
        if Liked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment.id)).exists():
            my_dict['Liked'].append(True)
        else:
            my_dict['Liked'].append(False)

        # Verify if disliked already
        if Disliked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment.id)).exists():
            my_dict['Disliked'].append(True)
        else:
            my_dict['Disliked'].append(False)
        
        # Count the likes
        comment_likes = Liked_Comment.objects.filter(comment_related_id=comment.id).count
        my_dict['L_count'].append(comment_likes)

        # Count the likes
        comment_dislikes = Disliked_Comment.objects.filter(comment_related_id=comment.id).count
        my_dict['D_count'].append(comment_dislikes)
        

        comment_list.append(my_dict)


    # Aim of the seed

    aim = {
        1: "To raise awarness",
        2: "To share a product or service",
        3: "To search for improvement",
        4: "To present theoretical results ",
        5: "To make laugh",
        6: "Others",
        }
    
    for keys in aim:
            if int(one_seed.aim_seed) == keys:
                aim = aim[keys]

    context = {
        "one_seed": one_seed, 
        "docu_seed": docu_seed, 
        "dislike": dislike,
        "sdg_seed_image": sdg_seed_image,
        "sdg_front": sdg_front,
        "value_chain_front": value_chain_front,
        "industry_front": industry_front,
        "comment_list": comment_list,
        "comment_seed": comment_seed,
        "form_comment": form_comment,
        "like_count": like_count,
        "dislike_count": dislike_count,
        "editable": editable,
        "fav": fav,
        "like": like,
        "aim": aim,
            }

    return render(request, "dist/inside/knowledge/seed/one_seed.html", context)


@login_required
def seed_edit(request, slug):
    """
    Aim - Edit a specific seed
    Description
    - Verify that user is allowed to perform this action
    - Get the seed that need to be edited using the slug that in provided in the button from the template
    - Retrieve the two forms used to create a seed (SeedForm - SeedFormVC) => not DocumentFormSeed since another edit function exits 
      instance = seed retrieved to have the existing data
    - Delete the retrieved seed and upload the new information
    - Return to the newly edited seed using the slug that was provided 
    - Add a message to show to the user

    """
    to_edit_seed = Seed.objects.get(slug=slug)
    if to_edit_seed.user.id != request.user.id:
        return render(request, 'dist/inside/knowledge/404_not_allowed.html')
    else:
        if request.method == 'POST':
            seed_form_edit = SeedForm(request.POST, request.FILES, instance=to_edit_seed)
            seed_vc_edit = SeedFormVC(request.POST)
            if seed_form_edit.is_valid() and seed_vc_edit.is_valid():
                seed = seed_form_edit.save(commit=False)
                seed.save()
                seed_form_edit.save_m2m()
                if Value_Chain_Seed.objects.filter(seed_id=to_edit_seed.id).exists():
                    f = Value_Chain_Seed.objects.filter(seed_id=to_edit_seed.id)
                    f.delete()
                    seed_vc_edit.instance.seed = to_edit_seed
                    seed_vc_edit.save()
                else:
                    seed_vc_edit.instance.seed = to_edit_seed
                    seed_vc_edit.save()
                messages.success(request,'Your seed was successfully updated!')
                return redirect(reverse(("knowledge:one_seed"),args=[to_edit_seed.slug]))
            else:
                seed_form_edit = SeedForm(request.POST, request.FILES, instance=to_edit_seed)
                seed_vc_edit = SeedFormVC(request.POST) 
        else:
            seed_form_edit = SeedForm(request.POST, request.FILES, instance=to_edit_seed)
            seed_vc_edit = SeedFormVC()
        return render(request, 'dist/inside/knowledge/seed/edit_seed.html', {
            'to_edit_seed': to_edit_seed,
            'seed_form_edit': seed_form_edit,
            'seed_vc_edit': seed_vc_edit,
        })  

from notifications.signals import notify

@login_required
def comment_add_like(request, pk):
    """
    Aim - Like a comment on a seed
    Description
    - Get the comment that need to be liked using the pk that in provided in the button from the template
    - If already liked remove the like and reduce the like_count of the comment
    - Else add the like and increase the like_count of the comment
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    comment_seed = Comment_Seed.objects.get(id=pk)
    if Liked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment_seed.id)).exists():
        Liked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment_seed.id)).delete()
    else:
        comment = Liked_Comment(user_related=request.user)
        comment.comment_related = comment_seed
        comment.save()
        if request.user != comment_seed.user:
            notify.send(request.user, recipient=comment_seed.user, verb="Like your seed")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def comment_add_dislike(request, pk):
    """
    Aim - Dislike a comment on a seed
    Description
    - Get the comment that need to be disliked using the pk that in provided in the button from the template
    - If already disliked remove the dislike of the comment
    - Else add the dislike of the comment
    - Return HTTP_REFERER to reload the page once the action is terminated

    """
    comment_seed = Comment_Seed.objects.get(id=pk)
    if Disliked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment_seed.id)).exists():
        Disliked_Comment.objects.filter(Q(user_related_id=request.user.id) & Q(comment_related_id=comment_seed.id)).delete()
    else:
        comment = Disliked_Comment(user_related=request.user)
        comment.comment_related = comment_seed
        comment.save()
        if request.user != comment_seed.user:
            notify.send(request.user, recipient=comment_seed.user, verb="Disike your seed")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def seed_delete_comment(request, pk):
    """
    Aim - Delete your comment on a seed
    Description 
    - Verify that user is allowed to perform this action
    - Get the comment that need to be deleted using the pk that in provided in the button from the template
    - Delete comment
    - Return HTTP_REFERER to reload the page once the action is terminated
    - Add a message to show to the user

    """
    comment_seed = Comment_Seed.objects.get(id=pk)
    if comment_seed.user != request.user:
        return render(request, 'dist/inside/knowledge/404_not_allowed.html')
    else:
        comment_seed.delete()
        messages.success(request, 'Your comment was successfully deleted!')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def seed_add_doc(request, slug):
    """
    Aim - Add a document on a seed
    Description
    - Verify that user is allowed to perform this action
    - Get the seed that need to be edited using the slug that in provided in the button from the template
    - Retrieve the form used to add a document to a seed (DocumentFormSeed) and connected it to the get a seed
    - Save document
    - Return to the newly edited seed using the slug that was provided 
    - Add a message to show to the user

    """
    seed = Seed.objects.get(slug=slug)
    if seed.user != request.user:
        return render(request, 'dist/inside/knowledge/404_not_allowed.html')
    else:
        if request.method == "POST":
            docu_form = DocumentFormSeed(request.POST, request.FILES)
            if docu_form.is_valid() : 
                docu_form.instance.seed_related = seed
                docu_form.save()
                messages.success(request, 'Your document was successfully add!')
                return redirect(reverse(("knowledge:one_seed"),args=[seed.slug]))
            else:
                messages.error(request, 'Something went wront, please correct it')
        else:
            docu_form = DocumentFormSeed(request.POST, request.FILES)

        return render(request, "dist/inside/knowledge/seed/add_document_seed.html", context={"seed": seed, "docu_form": docu_form, })


@login_required
def seed_delete_doc(request, pk):
    """
    Aim - Delete a seed
    Description
    - Verify that user is allowed to perform this action
    - Get the document that need to be deleted using the pk that in provided in the button from the template
    - Delete document
    - Return HTTP_REFERER to reload the page once the action is terminated
    - Add a message to show to the user
    """
    docu_seed = Document_Seed.objects.get(id=pk)
    related_seed = Seed.objects.get(id=docu_seed.seed_related_id)
    if related_seed.user != request.user:
        return render(request, 'dist/inside/knowledge/404_not_allowed.html')
    else:
        docu_seed.delete()
        messages.success(request, 'Your document was successfully deleted!')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def seed_delete(request, slug):
    """
    Aim - Delete a document on a seed
    Description
    - Verify that user is allowed to perform this action
    - Get the seed that need to be deleted using the slug that in provided in the button from the template
    - Delete seed
    - Return to the dashboard
    - Add a message to show to the user
    """
    seed = Seed.objects.get(slug=slug)
    if seed.user != request.user:
         return render(request, 'dist/inside/knowledge/404_not_allowed.html')
    else:
        if request.method == 'POST':
            seed_delete_form = SeedDeleteForm(request.POST, instance=seed)
            seed.delete()
            messages.success(request, 'Your seed was successfully deleted!')
            return redirect(reverse('dashboard:view_dashboard'))

        else:
            seed_delete_form = SeedDeleteForm(instance=seed)

        return render(request,'dist/inside/knowledge/seed/delete_seed.html', context={'seed_delete_form': seed_delete_form})


@login_required
def search_seed(request):
    """
    Aim - Search a seed based on the three classifier
    Description
    - Get the form to search a seed
    - In template the action is going to send the results to return_seed (next function)
    """
 
    seed_look = SearchSeed(request.GET)
    return render(request, "dist/inside/knowledge/seed/search_seed.html", context={"seed_look": seed_look})


@login_required
def return_seed(request):
    """
    Aim - Results of the search
    Description
    - Get the form to search a seed from the search_seed (previous function)
    - Verify is for is valid 
    - Retrieve all the objects connected to the wanted seed (sdg_info + value_chain_info + industry_info)
    - Retrieve all the objects for the design _front = want to have the name of the related classifier since the previous DB only ID
    - Retrieve the required seed from the databased using the if - elif statement. True = all of the classifier
    """
    if request.method == 'GET':
        form = SearchSeed(request.GET)

        if form.is_valid():
            sdg_info = request.GET.get('sdg_info')
            value_chain_info = request.GET.get('value_chain_info')
            industry_info = request.GET.get('industry_info')
            # For front_ design
            vc_search = Value_chain.objects.filter(id=value_chain_info)
            ind_search = Industry.objects.filter(id=industry_info)
            information_seed = []

            try:
                # all true 
                if sdg_info == "18" and value_chain_info == "1" and industry_info == "10":
                    seed_view = Seed.objects.all()
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except vc
                elif sdg_info == "18" and industry_info == "10":
                    value_chain_related = Value_Chain_Seed.objects.filter(value_chain_id=value_chain_info)
                    seed_view = Seed.objects.filter(id__in=[value_chain.seed_id for value_chain in value_chain_related])
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except ind
                elif sdg_info == "18" and value_chain_info == "1":
                    industry_related = Industry_Seed.objects.filter(industry_id=industry_info)
                    seed_view = Seed.objects.filter(id__in=[industry.seed_id for industry in industry_related])
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except sdg     
                elif value_chain_info == "1" and industry_info == "10":
                    sdg_related = SDG_Seed.objects.filter(sdg_id=sdg_info)
                    seed_view = Seed.objects.filter(Q(id__in=[sdg.seed_id for sdg in sdg_related]))
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except ind and vc
                elif sdg_info == "18":
                    industry_related = Industry_Seed.objects.filter(industry_id=industry_info)
                    value_chain_related = Value_Chain_Seed.objects.filter(value_chain_id=value_chain_info)
                    seed_view = Seed.objects.filter(Q(id__in=[value_chain.seed_id for value_chain in value_chain_related]) & Q(id__in=[industry.seed_id for industry in industry_related]))
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except ind and sdg      
                elif value_chain_info == "1":
                    sdg_related = SDG_Seed.objects.filter(sdg_id=sdg_info)
                    industry_related = Industry_Seed.objects.filter(industry_id=industry_info)
                    seed_view = Seed.objects.filter(Q(id__in=[sdg.seed_id for sdg in sdg_related]) & Q(id__in=[industry.seed_id for industry in industry_related]))
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all true except vc and sdg  
                elif industry_info == "10":
                    sdg_related = SDG_Seed.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_Seed.objects.filter(value_chain_id=value_chain_info)
                    seed_view = Seed.objects.filter(Q(id__in=[sdg.seed_id for sdg in sdg_related]) & Q(id__in=[value_chain.seed_id for value_chain in value_chain_related]))
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])

                # all wrong
                else:
                    sdg_related = SDG_Seed.objects.filter(sdg_id=sdg_info)
                    value_chain_related = Value_Chain_Seed.objects.filter(value_chain_id=value_chain_info)
                    industry_related = Industry_Seed.objects.filter(industry_id=industry_info)
                    seed_view = Seed.objects.filter(Q(id__in=[value_chain.seed_id for value_chain in value_chain_related]) & Q(id__in=[sdg.seed_id for sdg in sdg_related]) & Q(id__in=[industry.seed_id for industry in industry_related]))
                    author = User.objects.filter(id__in=[a.user_id for a in seed_view])


            except:
                seed_view = None


        else:
            form = SearchSeed(request.GET)

        return render(request, "dist/inside/knowledge/seed/return_seed.html", 
        context={
            "sdg_info": sdg_info,
            "vc_search": vc_search,
            "ind_search": ind_search,
            "seed_view": seed_view,
            "author": author,
            })


@login_required
def search_keywords_view(request):
    """
    Aim - Search a seed based on a keyword
    Description
    - Provide all the seeds
    - Get the form to search a seed with keywords
    - Sent the results to the same page and get the demanded keyword
    - Try to find the seeds with the keywords 
    - Except in case there are no results

    """
    seed = Seed.objects.order_by('-date_publication')
    form = SearchKeywords(request.GET)

    # Provide the search query
    if request.method == 'GET':
        form = SearchKeywords(request.GET)
        if form.is_valid():
            keywords = request.GET.get('keywords')
            try:
                tag = get_object_or_404(Tag, slug=keywords.lower())
                seeds_with_keywords = Seed.objects.filter(keywords=tag)
                vision_with_keywords = Vision.objects.filter(keywords=tag)
                user_author = User.objects.filter(Q(id__in=[uv.user_id for uv in vision_with_keywords]) | Q(id__in=[us.user_id for us in seeds_with_keywords]))
            except:
                seeds_with_keywords = "No seed"
                vision_with_keywords = "No vision"
        else:
            form = SearchKeywords(request.GET)
            seeds_with_keywords = "Not tried"
            vision_with_keywords = "Not tried"
    else:
        form = SearchKeywords()

    #Look for the search query
    aim = {
        1: "To raise awarness",
        2: "To share a product or service",
        3: "To search for improvement",
        4: "To present theoretical results ",
        5: "To make laugh",
        6: "Others",
        }

    list = []

    if seeds_with_keywords == "No seed" or seeds_with_keywords == "Not tried":
        pass
    else:
        for seed in seeds_with_keywords:
            my_dict = {'Type': [],'Name': [],'ID': [],'Date': [], 'Slug': [], 'Description': [],'Image': [],'Author': [], 'Aim': [], 'Likes': [],'Dislikes': [],}
            my_dict['Type'].append("Seed")
            my_dict['Name'].append(seed.title)
            my_dict['ID'].append(seed.id)
            my_dict['Date'].append(seed.date_publication)
            my_dict['Slug'].append(seed.slug)
            my_dict['Description'].append(seed.summary)
            my_dict['Image'].append(seed.profile_seed)
            # Find the author
            for user in user_author:
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
            
            list.append(my_dict)
    
    if vision_with_keywords == "No vision" or vision_with_keywords == "Not tried":
        pass
    else:
        for vision in vision_with_keywords:
            my_dict = {'Type': [], 'ID': [], 'Name': [] , 'Date': [], 'Slug': [], 'Content': [], 'Author': [], 'Aim': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
            my_dict['Type'].append("Vision")
            my_dict['ID'].append(vision.id)
            my_dict['Name'].append(vision.title)
            my_dict['Date'].append(vision.date_publication)
            my_dict['Slug'].append(vision.slug)
            my_dict['Content'].append(vision.content)
            # Find the author of the vision
            for user in user_author:
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
                            
            list.append(my_dict)


    return render(request, 'dist/inside/knowledge/seed/search_keywords.html', context = {'seed':seed,'form': form, 'seeds_with_keywords':seeds_with_keywords, "vision_with_keywords": vision_with_keywords, "list": list})


"""
----------------------- Functions for Vision --------------------------------------
- Create a vision: vision_create
- View a vision: view_vision
----------------------------------------------------------------------------------
""" 

@login_required
def vision_create(request):
    """
    Aim - Create a vision
    Description 
    - Retrieve the forms used to create a seed (VisionForm)
    - Verify its validity
    - Connect VisionForm to the reques.user
    - Save
    - Return to dashboard
    - Add a message to show to the user
    """
    if request.method == "POST":
        vision_form = VisionForm(request.POST)
        #common_tags = Vision.keywords.most_common()[:4]
        if vision_form.is_valid(): 
            vision_form.instance.user = request.user
            vision = vision_form.save(commit=False)
            vision.save()
            vision_form.save_m2m()
            messages.success(request, 'Your vision was successfully created!')
            return redirect('dashboard:view_dashboard')

        else:
            messages.error(request, 'Something went wrong, please correct it')

            
    else:
        vision_form = VisionForm()

        return render(request, "dist/inside/knowledge/vision/create_vision.html", context={"vision_form": vision_form,})


@login_required
def view_vision(request):
    visions = Vision.objects.all()
    return render(request, "dist/inside/knowledge/vision/view_all_vision.html", context={"visions": visions})
