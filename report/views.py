from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime, timedelta
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Bar, Pie
from django.contrib.auth.decorators import login_required

import pandas as pd

from knowledge.models import Seed, SDG_Seed, SDG, Value_chain, Value_Chain_Seed, Industry, Industry_Seed, Comment_Seed, Vision, Favourites_Seed, Liked_Seed
from accounts.models import Value_Chain_User, Industry_User, SDG_User, Follower

"""
----------------------- Functions for report --------------------------------------
- Access all the information needed for the report: report_create
- Export the report to csv: report_open
----------------------------------------------------------------------------------
"""
@login_required
def report_create(request):
    """
    Aim - Access all the information needed for the report
    Description 
    - Create a time frame
    - Apply this time frame to the seed - vision - comment_seed
    - Search the IND - SDG - VC for the following model:
        .Follower
        .Following
        .Favourites Seed
        .Liked Seed
    - Return information to create the dashboard 
    """
    last_year = datetime.today() - timedelta(days=365)
    last_2month = datetime.today() - timedelta(days=60)
    last_month = datetime.today() - timedelta(days=30)
    last_3weeks = datetime.today() - timedelta(days=21)
    last_2weeks = datetime.today() - timedelta(days=14)
    last_1weeks = datetime.today() - timedelta(days=7)

    "Seed information "
    # Total
    seed_count_total = Seed.objects.filter(user_id=request.user.id).count()
    #Year
    seed_count_year = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_year)).count()
    # 2 Month
    seed_count_2month = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2month)).count()
    # Month
    seed_count_month = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_month)).count()
    # 3 weeks
    seed_count_3weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_3weeks)).count()
    # 2 weeks
    seed_count_2weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2weeks)).count()
    # 1 weeks
    seed_count_1weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_1weeks)).count()

    x_data = ["Total", "Year", "2 Months", "Month", "3 Weeks", "2 Weeks", "1 Week"]
    y_data = [seed_count_total,seed_count_year,seed_count_2month,seed_count_month, seed_count_3weeks, seed_count_2weeks, seed_count_1weeks]
    plot_seed = plot([Bar(x=x_data, y=y_data)], output_type='div')

    "Vision Information"
    # Total
    vision_count_total = Vision.objects.filter(user_id=request.user.id).count()
    #Year
    vision_count_year = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_year)).count()
    # 2 Month
    vision_count_2month = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2month)).count()
    # Month
    vision_count_month = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_month)).count()
    # 3 Weeks
    vision_count_3weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_3weeks)).count()
    # 2 Weeks
    vision_count_2weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2weeks)).count()
    # 1 Weeks
    vision_count_1weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_1weeks)).count()

    
    x_data = ["Total", "Year", "2 Months", "Month", "3 Weeks", "2 Weeks", "1 Week"]
    y_data = [vision_count_total,vision_count_year,vision_count_2month,vision_count_month, vision_count_3weeks, vision_count_2weeks, vision_count_1weeks]
    plot_vision = plot([Bar(x=x_data, y=y_data, marker_color='green')], output_type='div')
 
    """ Comments """
    # Total
    comment_count_total = Comment_Seed.objects.filter(user_id=request.user.id).count()
    #Year
    comment_count_year = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_year)).count()
    # 2 Month
    comment_count_2month = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_2month)).count()
    # Month
    comment_count_month = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_month)).count()
    # 3 Weeks
    comment_count_3weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_3weeks)).count()
    # 2 Weeks
    comment_count_2weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_3weeks)).count()
    # 1 Weeks
    comment_count_1weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_1weeks)).count()


    x_data = ["Total", "Year", "2 Months", "Month", "3 Weeks", "2 Weeks", "1 Week"]
    y_data = [comment_count_total,comment_count_year,comment_count_2month,comment_count_month, comment_count_3weeks, comment_count_2weeks, comment_count_1weeks]
    plot_comments = plot([Bar(x=x_data, y=y_data, marker_color='blue')], output_type='div')

    """ Following """
    #Access the information on following 
    following = Follower.objects.filter(user_from_id=request.user.id)

    # Their sdgs
    list_sdg = []
    list_count = []
    for s in range(1,18):
        name = "SDG" + str(s)
        count_sdg = SDG_User.objects.filter(Q(user_id__in=[u.user_to_id for u in following]) & Q(sdg_id=s)).count()
        if count_sdg == 0:
            pass
        else:
            list_count.append(count_sdg)
            list_sdg.append(name)
            
    
    x_data = list_sdg
    y_data = list_count
    plot_sdg_following = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')

    # Their value_chain
    value_chain = Value_chain.objects.all()
    list_vc = []
    list_count = []
    for v in range(1,8):
        count_vc = Value_Chain_User.objects.filter(Q(user_id_id__in=[foll.user_to_id for foll in following]) & Q(value_chain_id=v)).count()
        if count_vc == 0:
            pass
        else:
            list_count.append(count_vc)
            for vc in value_chain:
                if v == vc.id:
                    list_vc.append(vc.title)

    x_data = list_vc
    y_data = list_count
    plot_vc_following = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')
    
    # Their value_chain
    industry = Industry.objects.all()
    list_ind = []
    list_count = []
    for i in range(1,8):
        industry_count = Industry_User.objects.filter(Q(user_id_id__in=[foll.user_to_id for foll in following]) & Q(industry_id=i)).count()
        if industry_count == 0:
            pass
        else:
            list_count.append(industry_count)
            for ind in industry:
                if i == ind.id:
                    list_ind.append(ind.title)

    x_data = list_ind
    y_data = list_count
    plot_ind_following = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')

    """ Followers """
    #Access the information on followers 
    follower = Follower.objects.filter(user_to_id=request.user.id)

    # Their sdgs
    list_sdg = []
    list_count = []
    for s in range(1,18):
        name = "SDG" + str(s)
        count_sdg = SDG_User.objects.filter(Q(user_id__in=[u.user_from_id for u in follower]) & Q(sdg_id=s)).count()
        if count_sdg == 0:
            pass
        else:
            list_sdg.append(name)
            list_count.append(count_sdg)
    
    x_data = list_sdg
    y_data = list_count
    plot_sdg_follower = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')

    # Their value_chain
    value_chain = Value_chain.objects.all()
    list_vc = []
    list_count = []
    for v in range(1,8):
        count_vc = Value_Chain_User.objects.filter(Q(user_id_id__in=[foll.user_from_id for foll in follower]) & Q(value_chain_id=v)).count()
        if count_vc == 0:
            pass
        else:
            list_count.append(count_vc)
            for vc in value_chain:
                if v == vc.id:
                    list_vc.append(vc.title)

    x_data = list_vc
    y_data = list_count
    plot_vc_follower = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 
    
    # Their industry
    industry = Industry.objects.all()
    list_ind = []
    list_count = []
    for i in range(1,8):
        industry_count = Industry_User.objects.filter(Q(user_id_id__in=[foll.user_from_id for foll in follower]) & Q(industry_id=i)).count()
        if industry_count == 0:
            pass
        else:
            list_count.append(industry_count)
            for ind in industry:
                if i == ind.id:
                    list_ind.append(ind.title)

    x_data = list_ind
    y_data = list_count
    plot_ind_follower = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 

    """ Favourties """
    fav_seed = Favourites_Seed.objects.filter(user_related_id=request.user.id)

    # related sdgs 
    list_sdg = []
    list_count = []
    for s in range(1,18):
        name = "SDG" + str(s)
        sdg_seed = SDG_Seed.objects.filter(Q(sdg_id=s) & Q(seed_id__in=[fv.seed_related_id for fv in fav_seed])).count()
        if sdg_seed == 0:
            pass
        else:
            list_sdg.append(name)
            list_count.append(sdg_seed)
    
    x_data = list_sdg
    y_data = list_count
    plot_sdg_favour = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')

    # related vc 
    value_chain = Value_chain.objects.all()
    list_vc = []
    list_count = []
    for v in range(1,8):
        vc_seed = Value_Chain_Seed.objects.filter(Q(seed_id__in=[fv.seed_related_id for fv in fav_seed]) & Q(value_chain_id=v)).count()
        if vc_seed == 0:
            pass
        else:
            list_count.append(vc_seed)
            for vc in value_chain:
                if v == vc.id:
                    list_vc.append(vc.title)

    x_data = list_vc
    y_data = list_count
    plot_vc_favour = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 

    # related ind
    industry = Industry.objects.all()
    list_ind = []
    list_count = []
    for i in range(1,8):
        ind_seed = Industry_Seed.objects.filter(Q(seed_id__in=[fv.seed_related_id for fv in fav_seed]) & Q(industry_id=i)).count()
        if ind_seed == 0:
            pass
        else:
            list_count.append(ind_seed)
            for ind in industry:
                if i == ind.id:
                    list_ind.append(ind.title)

    x_data = list_ind
    y_data = list_count
    plot_ind_favour = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 


    """ Likes """
    like_seed = Liked_Seed.objects.filter(user_related_id=request.user.id)

    # related sdgs 
    list_sdg = []
    list_count = []
    for s in range(1,18):
        name = "SDG" + str(s)
        sdg_seed = SDG_Seed.objects.filter(Q(sdg_id=s) & Q(seed_id__in=[li.seed_related_id for li in like_seed])).count()
        if sdg_seed == 0:
            pass
        else:
            list_sdg.append(name)
            list_count.append(sdg_seed)
    
    x_data = list_sdg
    y_data = list_count
    plot_sdg_likes = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div')

    # related vc 
    value_chain = Value_chain.objects.all()
    list_vc = []
    list_count = []
    for v in range(1,8):
        vc_seed = Value_Chain_Seed.objects.filter(Q(seed_id__in=[li.seed_related_id for li in like_seed]) & Q(value_chain_id=v)).count()
        if vc_seed == 0:
            pass
        else:
            list_count.append(vc_seed)
            for vc in value_chain:
                if v == vc.id:
                    list_vc.append(vc.title)

    x_data = list_vc
    y_data = list_count
    plot_vc_likes = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 

    # related ind
    industry = Industry.objects.all()
    list_ind = []
    list_count = []
    for i in range(1,8):
        ind_seed = Industry_Seed.objects.filter(Q(seed_id__in=[li.seed_related_id for li in like_seed]) & Q(industry_id=i)).count()
        if ind_seed == 0:
            pass
        else:
            list_count.append(ind_seed)
            for ind in industry:
                if i == ind.id:
                    list_ind.append(ind.title)

    x_data = list_ind
    y_data = list_count
    plot_ind_likes = plot([Pie(labels=x_data, values=y_data, textinfo='label+percent',
                             insidetextorientation='radial')], output_type='div') 

    return render(request, "dist/inside/report.html", context={
        'plot_seed': plot_seed, 'seed_count_total': seed_count_total,
        'plot_vision': plot_vision, 'vision_count_total': vision_count_total,
        'plot_comments': plot_comments, 'comment_count_total': comment_count_total,
        'following': following.count(),'plot_sdg_following': plot_sdg_following, 'plot_vc_following': plot_vc_following,'plot_ind_following': plot_ind_following,
        'follower': follower.count(),'plot_sdg_follower': plot_sdg_follower,'plot_vc_follower': plot_vc_follower,'plot_ind_follower': plot_ind_follower,
        'fav_seed': fav_seed.count(),'plot_sdg_favour':plot_sdg_favour,'plot_vc_favour':plot_vc_favour,'plot_ind_favour':plot_ind_favour,
        'like_seed': like_seed.count(), 'plot_sdg_likes': plot_sdg_likes, 'plot_vc_likes': plot_vc_likes, 'plot_ind_likes': plot_ind_likes})


@login_required
def report_open(request):
    """
    Aim - Access all the information needed for the report
    Description 
    - Create a time frame
    - Apply this time frame to the seed - vision - comment_seed
    - Search the IND - SDG - VC for the following model:
        .Follower
        .Following
        .Favourites Seed
        .Liked Seed
    - Export to CSV
    """
    last_year = datetime.today() - timedelta(days=365)
    last_2month = datetime.today() - timedelta(days=60)
    last_month = datetime.today() - timedelta(days=30)
    last_3weeks = datetime.today() - timedelta(days=21)
    last_2weeks = datetime.today() - timedelta(days=14)
    last_1weeks = datetime.today() - timedelta(days=7)

    data_frame = pd.DataFrame(columns=['Type_Info','Level_Info', 'Count',])

    """ Seed """
    # Total
    seed_count_total = Seed.objects.filter(user_id=request.user.id).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_total', 'Count':seed_count_total}
    data_frame = data_frame.append(new_row, ignore_index=True)
    #Year
    seed_count_year = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_year)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_year', 'Count': seed_count_year}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 2 Month
    seed_count_2month = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2month)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_2month', 'Count':seed_count_2month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # Month
    seed_count_month = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_month)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_month', 'Count':seed_count_month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 3 Weeks
    seed_count_3weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_3weeks)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_3weeks', 'Count':seed_count_3weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 2 Weeks
    seed_count_2weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2weeks)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_2weeks', 'Count':seed_count_2weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 1 Weeks
    seed_count_1weeks = Seed.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_1weeks)).count()
    new_row = {'Type_Info':'Seed','Level_Info':'seed_count_1weeks', 'Count':seed_count_1weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    

    """ Vision """
    # Total
    vision_count_total = Vision.objects.filter(user_id=request.user.id).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_total', 'Count':vision_count_total}
    data_frame = data_frame.append(new_row, ignore_index=True)
    #Year
    vision_count_year = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_year)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_year', 'Count':vision_count_year}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 2 Month
    vision_count_2month = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2month)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_2month', 'Count':vision_count_2month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # Month
    vision_count_month = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_month)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_month', 'Count':vision_count_month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 3 Weeks
    vision_count_3weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_3weeks)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_3weeks', 'Count':vision_count_3weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # Month
    vision_count_2weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_2weeks)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_2weeks', 'Count':vision_count_2weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # Month
    vision_count_1weeks = Vision.objects.filter(Q(user_id=request.user.id) & Q(date_publication__gte=last_1weeks)).count()
    new_row = {'Type_Info':'Vision','Level_Info':'vision_count_1weeks', 'Count':vision_count_1weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)


    """ Comments """
    # Total
    comment_count_total = Comment_Seed.objects.filter(user_id=request.user.id).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_total', 'Count':comment_count_total}
    data_frame = data_frame.append(new_row, ignore_index=True)
    #Year
    comment_count_year = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_year)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_year', 'Count':comment_count_year}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 2 Month
    comment_count_2month = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_2month)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_2month', 'Count':comment_count_2month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # Month
    comment_count_month = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_month)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_month', 'Count':comment_count_month}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 3 Weeks
    comment_count_3weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_3weeks)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_3weeks', 'Count':comment_count_3weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 2 Weeks
    comment_count_2weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_2weeks)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_2weeks', 'Count':comment_count_2weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)
    # 1 Weeks
    comment_count_1weeks = Comment_Seed.objects.filter(Q(user_id=request.user.id) & Q(date_posted__gte=last_1weeks)).count()
    new_row = {'Type_Info':'Comment','Level_Info':'comment_count_1weeks', 'Count':comment_count_1weeks}
    data_frame = data_frame.append(new_row, ignore_index=True)

    """ Following """
    #Access the information on following 
    following = Follower.objects.filter(user_from_id=request.user.id)
    new_row = {'Type_Info':'Following','Level_Info':'following_count', 'Count': following.count()}
    data_frame = data_frame.append(new_row, ignore_index=True)

    # Their sdgs
    sdg = SDG.objects.all()
    for s in range(1,18):
        count_sdg = SDG_User.objects.filter(Q(user_id__in=[u.user_to_id for u in following]) & Q(sdg_id=s)).count()
        for sdgs in sdg:
            if s == sdgs.id:
                name = sdgs.title
                new_row = {'Type_Info':'Following_SDG','Level_Info':name, 'Count': count_sdg}
                data_frame = data_frame.append(new_row, ignore_index=True)

    # Their value_chain
    value_chain = Value_chain.objects.all()
    for v in range(1,8):
        count_vc = Value_Chain_User.objects.filter(Q(user_id_id__in=[foll.user_to_id for foll in following]) & Q(value_chain_id=v)).count()
        for vc in value_chain:
            if v == vc.id:
                name = vc.title
                new_row = {'Type_Info':'Following_VC','Level_Info':name, 'Count': count_vc}
                data_frame = data_frame.append(new_row, ignore_index=True)
    
    # Their industry
    industry = Industry.objects.all()
    for i in range(1,8):
        industry_count = Industry_User.objects.filter(Q(user_id_id__in=[foll.user_to_id for foll in following]) & Q(industry_id=i)).count()
        for ind in industry:
            if i == ind.id:
                name = ind.title
                new_row = {'Type_Info':'Following_IND','Level_Info':name, 'Count': industry_count}
                data_frame = data_frame.append(new_row, ignore_index=True)
    

    """ Followers """
    #Access the information on followers 
    follower = Follower.objects.filter(user_to_id=request.user.id)
    new_row = {'Type_Info':'Follower','Level_Info':'follower_count', 'Count': follower.count()}
    data_frame = data_frame.append(new_row, ignore_index=True)

    # Their sdgs
    for s in range(1,18):
        count_sdg = SDG_User.objects.filter(Q(user_id__in=[u.user_from_id for u in follower]) & Q(sdg_id=s)).count()
        for sdgs in sdg:
            if s == sdgs.id:
                name = sdgs.title
                new_row = {'Type_Info':'Follower_SDG','Level_Info':name, 'Count': count_sdg}
                data_frame = data_frame.append(new_row, ignore_index=True)

    # Their value_chain
    for v in range(1,8):
        count_vc = Value_Chain_User.objects.filter(Q(user_id_id__in=[foll.user_from_id for foll in following]) & Q(value_chain_id=v)).count()
        for vc in value_chain:
            if v == vc.id:
                name = vc.title
                new_row = {'Type_Info':'Follower_VC','Level_Info':name, 'Count': count_vc}
                data_frame = data_frame.append(new_row, ignore_index=True)
  

    # Their industry
    for i in range(1,8):
        industry_count = Industry_User.objects.filter(Q(user_id_id__in=[foll.user_from_id for foll in following]) & Q(industry_id=i)).count()
        for ind in industry:
            if i == ind.id:
                name = ind.title
                new_row = {'Type_Info':'Follower_IND','Level_Info':name, 'Count': industry_count}
                data_frame = data_frame.append(new_row, ignore_index=True)

    
    """ Favourties """
    fav_seed = Favourites_Seed.objects.filter(user_related_id=request.user.id)
    new_row = {'Type_Info':'Favourites Seed','Level_Info':'fav_seed_count', 'Count': fav_seed.count()}
    data_frame = data_frame.append(new_row, ignore_index=True)

    # related sdgs 
    for s in range(1,18):
        sdg_seed = SDG_Seed.objects.filter(Q(sdg_id=s) & Q(seed_id__in=[fv.seed_related_id for fv in fav_seed])).count()
        for sdgs in sdg:
            if s == sdgs.id:
                name = sdgs.title
                new_row = {'Type_Info':'Favourites_Seed_SDG','Level_Info':name, 'Count': sdg_seed}
                data_frame = data_frame.append(new_row, ignore_index=True)

    # related vc 
    for v in range(1,8):
        vc_seed = Value_Chain_Seed.objects.filter(Q(seed_id__in=[fv.seed_related_id for fv in fav_seed]) & Q(value_chain_id=v)).count()
        for vc in value_chain:
            if v == vc.id:
                name = vc.title
                new_row = {'Type_Info':'Favourites_Seed_VC','Level_Info':name, 'Count': vc_seed}
                data_frame = data_frame.append(new_row, ignore_index=True)

    # related ind
    list_fav_ind = []
    for i in range(1,8):
        ind_seed = Industry_Seed.objects.filter(Q(seed_id__in=[fv.seed_related_id for fv in fav_seed]) & Q(industry_id=i)).count()
        for ind in industry:
            if i == ind.id:
                name = ind.title
                new_row = {'Type_Info':'Favourites_Seed_IND','Level_Info':name, 'Count': ind_seed}
                data_frame = data_frame.append(new_row, ignore_index=True)


    """ Likes """
    like_seed = Liked_Seed.objects.filter(user_related_id=request.user.id)
    new_row = {'Type_Info':'Seed Likes','Level_Info':'like_seed_count', 'Count': like_seed.count()}
    data_frame = data_frame.append(new_row, ignore_index=True)

    # related sdgs 
    list_like_sdg = []
    for s in range(1,18):
        sdg_seed = SDG_Seed.objects.filter(Q(sdg_id=s) & Q(seed_id__in=[li.seed_related_id for li in like_seed])).count()
        for sdgs in sdg:
            if s == sdgs.id:
                name = sdgs.title
                new_row = {'Type_Info':'Seed_Liked_SDG','Level_Info':name, 'Count': sdg_seed}
                data_frame = data_frame.append(new_row, ignore_index=True)

    # related vc 
    list_like_vc = []
    for v in range(1,8):
        vc_seed = Value_Chain_Seed.objects.filter(Q(seed_id__in=[li.seed_related_id for li in like_seed]) & Q(value_chain_id=v)).count()
        if v == vc.id:
            name = vc.title
            new_row = {'Type_Info':'Seed_Liked_VC','Level_Info':name, 'Count': vc_seed}
            data_frame = data_frame.append(new_row, ignore_index=True)

    # related ind
    list_like_ind = []
    for i in range(1,8):
        ind_seed = Industry_Seed.objects.filter(Q(seed_id__in=[li.seed_related_id for li in like_seed]) & Q(industry_id=i)).count()
        for ind in industry:
            if i == ind.id:
                name = ind.title
                new_row = {'Type_Info':'Seed_Liked_IND','Level_Info':name, 'Count': ind_seed}
                data_frame = data_frame.append(new_row, ignore_index=True)
               
    ### Information to save the file 
    _datetime = datetime.now()
    datetime_str = _datetime.strftime("%Y-%m-%d")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={0}{1}{2}{3}.csv'.format("report - ",request.user.username," - ",datetime_str)
    data_frame.to_csv(path_or_buf=response)  # with other applicable parameters
    return response


    