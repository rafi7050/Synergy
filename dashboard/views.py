from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from knowledge.models import Seed, SDG_Seed, Value_Chain_Seed, Industry_Seed, Comment_Seed, Vision, Favourites_Seed, Liked_Seed, Disliked_Seed, Liked_Vision, Disliked_Vision, Disliked_Comment, Liked_Comment
from accounts.models import User, Profile, Value_Chain_User, Industry_User, SDG_User, Follower, Feedback, Liked_Feedback, Disliked_Feedback

"""
----------------------- Functions for Dashboard --------------------------------------
- Sort the list for the dashboard based on the date: myFunc
- View all the feeds - news for an user: view_dashboard
--------------------------------------------------------------------------------------
"""

# Sort the list based on data
@login_required
def myFunc(e):
    """
    Aim - Sort the list for the dashboard based on the date
    Description
        Return least recent item
    """
    return e['Date']

@login_required
def view_dashboard(request):
    """
    Aim - View all the feeds - news for an user
    Description
    - Find the filters that can interest an user:
        .based on his/her interest
        .based on the person he/she is following
    - Find the information related to those filters for:
        .seed
        .new user
        .vision
        .feedback
        .comment on a seed
        .new follower
        .fav/liked seed
        .liked vision
    - Return those information

    """
    # Find all sdgs and ind the user is interested in
    sdg_user = SDG_User.objects.filter(user_id_id=request.user.id)
    ind_user = Industry_User.objects.filter(user_id_id=request.user.id)
    vc_user = Value_Chain_User.objects.filter(user_id_id=request.user.id)

    # Find all following of user
    following = Follower.objects.filter(user_from_id=request.user.id)


    # Find related seed 
    sdg_seed = SDG_Seed.objects.filter(sdg_id__in=[sdg.sdg_id for sdg in sdg_user])
    ind_seed = Industry_Seed.objects.filter(industry_id__in=[ind.industry_id for ind in ind_user])
    vc_seed = Value_Chain_Seed.objects.filter(value_chain_id__in=[vc.value_chain_id for vc in vc_user])
    seed_interest = Seed.objects.filter(
        Q(id__in=[see.seed_id for see in sdg_seed]) |
        Q(id__in=[se.seed_id for se in ind_seed]) |
        Q(id__in=[s.seed_id for s in vc_seed]) |
        Q(user_id__in=[e.user_to_id for e in following]) | 
        Q(user_id=request.user.id)
        ).order_by('-date_publication')[:30]
    other_profile_seed = Profile.objects.filter(id__in=[use.user_id for use in seed_interest])


    # Find related user
    sdg_other_user = SDG_User.objects.filter(sdg_id__in=[s.sdg_id for s in sdg_user])
    ind_other_user = Industry_User.objects.filter(industry_id__in=[i.industry_id for i in ind_user])
    vc_other_user = Value_Chain_User.objects.filter(value_chain_id__in=[v.value_chain_id for v in vc_user])
    other_user = User.objects.filter(
        Q(id__in=[use.user_id_id for use in sdg_other_user]) |
        Q(id__in=[us.user_id_id for us in ind_other_user]) |
        Q(id__in=[u.user_id_id for u in vc_other_user])
        ).exclude(id=request.user.id)[:30]
    other_profile_user = Profile.objects.filter(id__in=[use.id for use in other_user])


    # Find related vision
    vision_following = Vision.objects.filter(
        Q(user_id__in=[e.user_to_id for e in following]) |
        Q(user_id=request.user.id)
        )[:30]
    other_profile_vision = Profile.objects.filter(id__in=[u.user_id for u in vision_following])
   

    # Find related feedback
    feedback = Feedback.objects.filter(
        Q(to_user_id=request.user.id) |
        Q(to_user_id__in=[user.user_to_id for user in following]) |
        Q(from_user_id__in=[user.user_to_id for user in following])
        )[:30]
    other_user_feedback = User.objects.filter(
        Q(id__in=[u.from_user_id for u in feedback]) |
        Q(id__in=[u.to_user_id for u in feedback]))


    # Find related comments for seed
    seed_user = Seed.objects.filter(user_id=request.user.id)
    comment_user = Comment_Seed.objects.filter(user_id=request.user.id) 
    comment_seed = Comment_Seed.objects.filter(
        Q(seed_connected_id__in=[cs.id for cs in seed_user]) |
        Q(parent_id__in=[cu.id for cu in comment_user]) |
        Q(user_id__in=[cs.user_to_id for cs in following])
    )[:30]
    other_user_comment_seed = User.objects.filter(id__in=[ucs.user_id for ucs in comment_seed])
    other_seed_comment_seed = Seed.objects.filter(id__in=[scs.seed_connected_id for scs in comment_seed])


    # Find who is following who
    new_following = Follower.objects.filter(
        Q(user_to_id=request.user.id) |
        Q(user_from_id__in=[user.user_to_id for user in following])
        )[:30]
    other_user_follower = User.objects.filter(Q(id__in=[u.user_from_id for u in new_following]) | Q(id__in=[u.user_to_id for u in new_following])) 
    other_profile_follower = Profile.objects.filter(id__in=[ouf.id for ouf in other_user_follower])

    # Find new favorites seed from user we are following
    seed_user_favourites = Favourites_Seed.objects.filter(user_related_id__in=[sf.user_to_id for sf in following])
    user_favourites = User.objects.filter(id__in=[usf.user_related_id for usf in seed_user_favourites]) 
    seed_favourites = Seed.objects.filter(id__in=[sf.seed_related_id for sf in seed_user_favourites]) 
    author_seed = User.objects.filter(id__in=[au.user_id for au in seed_favourites])
    
    # Find seed that were liked from user we are following
    seed_user_likes = Liked_Seed.objects.filter(user_related_id__in=[sf.user_to_id for sf in following])
    user_likes = User.objects.filter(id__in=[usf.user_related_id for usf in seed_user_likes]) 
    seed_likes = Seed.objects.filter(id__in=[sf.seed_related_id for sf in seed_user_likes]) 
    author_seed_l = User.objects.filter(id__in=[au.user_id for au in seed_likes])

    # Find vision that were liked from user we are following
    vision_user_likes = Liked_Vision.objects.filter(user_related_id__in=[vf.user_to_id for vf in following])
    user_v_likes = User.objects.filter(id__in=[usf.user_related_id for usf in vision_user_likes]) 
    vision_liked = Vision.objects.filter(id__in=[vf.vision_related_id for vf in vision_user_likes]) 
    author_vision_l = User.objects.filter(id__in=[auv.user_id for auv in vision_liked])
    author_vision_l_profile = Profile.objects.filter(id__in=[avlp.id for avlp in author_vision_l])
    

    # Find information about user
    user_information = User.objects.all()
    types = {
        1: "Governement",
        2: "NGOs",
        3: "Social Venture",
        4: "Organization",
        5: "Financial Institution",
        6: "University",
        7: "Experts",
        8: "Platform Monitors",
        9: "Others",
        }

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

    # 1. Provide needed information for user   
    for user in other_user:
        my_dict = {'Type': [],'NBR': [],'Name': [] ,'Image': [], 'Location': [], 'Date': [], 'Description': [], 'Aim': []}
        my_dict['Type'].append("User")
        my_dict['NBR'].append(x)
        my_dict['Name'].append(user.username)
        my_dict['Date'].append(user.date_joined)

        # Find the associated profile 
        for profile in other_profile_user:
            if user.id == int(profile.id):
                my_dict['Description'].append(profile.description)
                my_dict['Image'].append(profile.profile_picture)
                my_dict['Location'].append(profile.country)
                for keys in types:
                    if int(profile.type_user) == keys:
                        my_dict['Aim'].append(types[keys])

        x += 1
        list.append(my_dict)


    # 2. Provide needed information for feedback
    for user_feedback in feedback:
        my_dict = {'Type': [],'NBR': [],'ID': [], 'Date': [], 'Content': [], 'From': [], 'To': [], 'Likes': [],'Dislikes': [], 'L': [],'D': [] }
        my_dict['Type'].append("Feedback")
        my_dict['ID'].append(user_feedback.id)
        my_dict['NBR'].append(x)
        my_dict['Date'].append(user_feedback.created)
        my_dict['Content'].append(user_feedback.content)
        for u in other_user_feedback:
            if u.id == int(user_feedback.to_user_id):
                my_dict['To'].append(u.username)
            elif u.id == int(user_feedback.from_user_id):
                my_dict['From'].append(u.username)


        #Counts the likes
        user_feedback_likes = Liked_Feedback.objects.filter(feedback_related_id=user_feedback.id).count
        my_dict['Likes'].append(user_feedback_likes)

        #Counts the dislikes
        user_feedback_dislikes = Disliked_Feedback.objects.filter(feedback_related_id=user_feedback.id).count
        my_dict['Dislikes'].append(user_feedback_dislikes)

        # Look if the comment was already liked or not 
        if Liked_Feedback.objects.filter(Q(feedback_related_id=user_feedback.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        if Disliked_Feedback.objects.filter(Q(feedback_related_id=user_feedback.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")

        x += 1
        list.append(my_dict)


    # 3. Provide needed information for seed
    for seed in seed_interest:
        my_dict = {'Type': [], 'ID': [],'NBR': [],'Name': [] , 'Date': [], 'Slug': [],'Image': [], 'Description': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [],}
        my_dict['Type'].append("Seed")
        my_dict['ID'].append(seed.id)
        my_dict['NBR'].append(x)
        my_dict['Name'].append(seed.title)
        my_dict['Date'].append(seed.date_publication)
        my_dict['Slug'].append(seed.slug)
        my_dict['Image'].append(seed.profile_seed)
        my_dict['Description'].append(seed.summary)
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

        # Look for the information of the user who created the seed
        for user in user_information:
            if user.id == int(seed.user_id):
                my_dict['User'].append(user.username)
                # Find the associated profile 
                for profile in other_profile_seed:
                    if user.id == int(profile.id):
                        for key in types:
                            if int(profile.type_user) == key:
                                my_dict['User_Type'].append(types[key])
        

        x += 1
        list.append(my_dict)


    # 4. Provide needed information for vision
    for vision in vision_following:
        my_dict = {'Type': [], 'ID': [],'NBR': [],'Name': [] , 'Date': [], 'Slug': [], 'Content': [], 'Aim': [], 'User': [], 'User_Type': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
        my_dict['Type'].append("Vision")
        my_dict['ID'].append(vision.id)
        my_dict['NBR'].append(x)
        my_dict['Name'].append(vision.title)
        my_dict['Date'].append(vision.date_publication)
        my_dict['Slug'].append(vision.slug)
        my_dict['Content'].append(vision.content)
        #my_dict['Aim'].append(vision.aim_vision)
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
        if Liked_Vision.objects.filter(Q(vision_related_id=vision.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        
        if Disliked_Vision.objects.filter(Q(vision_related_id=vision.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")

        # Look for the information of the user who created the vision
        for use in user_information:
            if use.id == int(vision.user_id):
                my_dict['User'].append(use.username)
                # Find the associated profile 
                for profile_vision in other_profile_vision:
                    if use.id == int(profile_vision.id):
                        for key in types:
                            if int(profile_vision.type_user) == key:
                                my_dict['User_Type'].append(types[key])
                


        x += 1
        list.append(my_dict)


    # 5. Provide needed information for comment on seed
    for com_s in comment_seed:
        my_dict = {'Type': [],'NBR': [],'ID': [], 'Date': [], 'Content': [], 'From_User': [], 'To_Seed': [],'Image': [],'Summary': [], 'Slug': [], 'Likes': [],'Dislikes': [], 'L': [],'D': [] }
        my_dict['Type'].append("Comment_Seed")
        my_dict['ID'].append(com_s.id)
        my_dict['NBR'].append(x)
        my_dict['Date'].append(com_s.date_posted)
        my_dict['Content'].append(com_s.content)
        for u in other_user_comment_seed:
            if u.id == int(com_s.user_id):
                my_dict['From_User'].append(u.username)

        for s in other_seed_comment_seed:
            if s.id == int(com_s.seed_connected_id):
                my_dict['To_Seed'].append(s.title)
                my_dict['Image'].append(s.profile_seed)
                my_dict['Summary'].append(s.summary)
                my_dict['Slug'].append(s.slug)

        #Counts the likes
        user_comment_seed_likes = Liked_Comment.objects.filter(comment_related_id=com_s.id).count
        my_dict['Likes'].append(user_comment_seed_likes)


        #Counts the dislikes
        user_comment_seed_dislikes = Disliked_Comment.objects.filter(comment_related_id=com_s.id).count
        my_dict['Dislikes'].append(user_comment_seed_dislikes)


        # Look if the comment was already liked or not 
        if Liked_Comment.objects.filter(Q(comment_related_id=com_s.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['L'].append("Yes")
        else:
            my_dict['L'].append("No")
        
        
        if Disliked_Comment.objects.filter(Q(comment_related_id=com_s.id) & Q(user_related_id=request.user.id)).exists():
            my_dict['D'].append("Yes")
        else:
            my_dict['D'].append("No")


        x += 1
        list.append(my_dict)


    # 6. Provide needed information on new followers from people we are following
    for user_follower in new_following:
        my_dict = {'Type': [],'NBR': [],'ID': [], 'Date': [], 'Content': [], 'From': [], 'To': [], 'To_Pic': [], 'From_Pic': []}
        my_dict['Type'].append("New_Follower")
        my_dict['ID'].append(user_follower.id)
        my_dict['NBR'].append(x)
        my_dict['Date'].append(user_follower.created)
        for u in other_user_follower:
            if u.id == int(user_follower.user_to_id):
                my_dict['To'].append(u.username)
                for p in other_profile_follower: 
                    if int(p.id) == u.id:
                        my_dict['To_Pic'].append(p.profile_picture)
            elif u.id == int(user_follower.user_from_id):
                my_dict['From'].append(u.username)
                for p in other_profile_follower: 
                    if int(p.id) == u.id:
                         my_dict['From_Pic'].append(p.profile_picture)
               

        x += 1
        list.append(my_dict)


    # 7. Provide needed information on new favourites from people we are following
    for seed_user in seed_user_favourites:
        my_dict = {'Type': [], 'ID': [],'NBR': [],'Name': [] ,'Date': [], 'Date_Pub': [], 'Slug': [], 'Description': [], 'Image': [], 'Aim': [], 'User_Fav': [], 'User_Seed': [], 'Likes': [],'Dislikes': [],}
        my_dict['Date'].append(seed_user.created)
        my_dict['Type'].append("Fav_Seed")
        my_dict['NBR'].append(x)
        # Find the user who liked the seed
        for user in user_favourites:
            if user.id == seed_user.user_related_id:
                my_dict['User_Fav'].append(user.username)

        # Find the related seed
        for s_fav in seed_favourites:
            if s_fav.id == seed_user.seed_related_id:
                my_dict['ID'].append(s_fav.id)
                my_dict['Name'].append(s_fav.title)
                my_dict['Date_Pub'].append(s_fav.date_publication)
                my_dict['Slug'].append(s_fav.slug)
                my_dict['Description'].append(s_fav.summary)
                my_dict['Image'].append(s_fav.profile_seed)
                # Find the username of the author
                for sa in author_seed:
                    if sa.id == s_fav.user_id:
                        my_dict['User_Seed'].append(sa.username)
                # Find the real title of the aim
                for keys in aim:
                    if int(s_fav.aim_seed) == keys:
                        my_dict['Aim'].append(aim[keys])

                #Counts the likes
                seed_fav_likes = Liked_Seed.objects.filter(seed_related_id=s_fav.id).count
                my_dict['Likes'].append(seed_fav_likes)

                #Counts the dislikes
                seed_fav_dislikes = Disliked_Seed.objects.filter(seed_related_id=s_fav.id).count
                my_dict['Dislikes'].append(seed_fav_dislikes)

        x += 1
        list.append(my_dict)
    

    # 8. Provide needed information on new seed liked from people we are following
    for seed_l in seed_user_likes:
        my_dict = {'Type': [], 'ID': [],'NBR': [],'Name': [] ,'Date': [], 'Date_Pub': [], 'Slug': [], 'Description': [], 'Image': [], 'Aim': [], 'User_L': [], 'User_Seed': [], 'Likes': [],'Dislikes': [],}
        my_dict['Date'].append(seed_l.created)
        my_dict['Type'].append("Liked_Seed")
        my_dict['NBR'].append(x)
        # Find the user who liked the seed
        for user in user_likes:
            if user.id == seed_l.user_related_id:
                my_dict['User_L'].append(user.username)

        # Find the related seed
        for s_l in seed_favourites:
            if s_l.id == seed_l.seed_related_id:
                my_dict['ID'].append(s_l.id)
                my_dict['Name'].append(s_l.title)
                my_dict['Date_Pub'].append(s_l.date_publication)
                my_dict['Slug'].append(s_l.slug)
                my_dict['Description'].append(s_l.summary)
                my_dict['Image'].append(s_l.profile_seed)
                # Find the username of the author
                for s in author_seed_l:
                    if s.id == s_l.user_id:
                        my_dict['User_Seed'].append(s.username)
                # Find the real title of the aim
                for keys in aim:
                    if int(s_l.aim_seed) == keys:
                        my_dict['Aim'].append(aim[keys])

                #Counts the likes
                seed_l_likes = Liked_Seed.objects.filter(seed_related_id=s_l.id).count
                my_dict['Likes'].append(seed_l_likes)

                #Counts the dislikes
                seed_l_dislikes = Disliked_Seed.objects.filter(seed_related_id=s_l.id).count
                my_dict['Dislikes'].append(seed_l_dislikes)


        x += 1
        list.append(my_dict)
 

    # 9. Provide needed information on new vision liked from people we are following
    for visio_l in vision_user_likes:
        my_dict = {'Type': [],'Date': [],'NBR': [], 'User_L': [], 'ID': [],'Name': [] , 'Date_Pub': [], 'Slug': [], 'Content': [], 'Aim': [], 'User_Vision': [], 'User_Type_Vision': [], 'Likes': [],'Dislikes': [], 'L': [],'D': []}
        my_dict['Type'].append("Vision_Liked")
        my_dict['Date'].append(visio_l.created)
        my_dict['NBR'].append(x)
        # Find the user who liked the vision
        for user_v in user_v_likes:
            if user_v.id == visio_l.user_related_id:
                my_dict['User_L'].append(user_v.username)

        # Find the information on the related vision
        for v_l in vision_liked:
            if v_l.id == visio_l.vision_related_id:
                my_dict['ID'].append(v_l.id)
                my_dict['Name'].append(v_l.title)
                my_dict['Date_Pub'].append(v_l.date_publication)
                my_dict['Slug'].append(v_l.slug)
                my_dict['Content'].append(v_l.content)
            try:
                for keys in aim:
                    if int(v_l.aim_vision) == keys:
                        my_dict['Aim'].append(aim[keys])
            except:
                my_dict['Aim'].append("No Aim provided")

            # Find the username of the author
            for v in author_vision_l:
                if v.id == v_l.user_id:
                    my_dict['User_Vision'].append(v.username)
                    try:
                        for p in author_vision_l_profile:
                            if int(p.id) == v.id:
                                for key in types:
                                    if int(p.type_user) == key:
                                        my_dict['User_Type_Vision'].append(types[key])
                    except:
                        my_dict['User_Type_Vision'].append("No type provided by the user")

            #Counts the likes
            vision_likes = Liked_Vision.objects.filter(vision_related_id=v_l.id).count
            my_dict['Likes'].append(vision_likes)

            #Counts the dislikes
            vision_dislikes = Disliked_Vision.objects.filter(vision_related_id=v_l.id).count
            my_dict['Dislikes'].append(vision_dislikes)

            # Look if the comment was already liked or not 
            if Liked_Vision.objects.filter(Q(vision_related_id=v_l.id) & Q(user_related_id=request.user.id)).exists():
                my_dict['L'].append("Yes")
            else:
                my_dict['L'].append("No")
            
            
            if Disliked_Vision.objects.filter(Q(vision_related_id=v_l.id) & Q(user_related_id=request.user.id)).exists():
                my_dict['D'].append("Yes")
            else:
                my_dict['D'].append("No")

        x += 1
        list.append(my_dict)


    #list.sort(key=myFunc, reverse=True)

    return render(request, "dist/inside/dashboard.html", context={"list": list, "vision_following":vision_following, "seed_interest": seed_interest})
