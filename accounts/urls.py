from django.urls import path, include
from django.contrib.auth import login, logout, authenticate

from . import views

# name of the app when calling it externally
app_name = "accounts"

urlpatterns = [
    path("create/", views.user_register, name="create_user"),
    path("logout/", views.logout_request, name="logout"),
    path("login/", views.login_request, name="login"),
    #path("login/dashboard/", views.dashboard, name="dashboard"),
    path("profile/user/<str:username>/", views.user_profile, name="user_profile"),
    path("profile/edit_profile/", views.edit_profile, name="edit_profile"),
    path("profile/edit_password/", views.edit_password, name="edit_password"),
    path("profile/seed_add_favourite/<slug:slug>/", views.seed_add_fav, name="seed_add_fav"),
    path("profile/seed_add_like/<slug:slug>/", views.seed_add_like, name="seed_add_like"),
    path("profile/seed_add_dislike/<slug:slug>/", views.seed_add_dislike, name="seed_add_dislike"),
    path("profile/vision_add_like/<slug:slug>/", views.vision_add_like, name="vision_add_like"),
    path("profile/vision_add_dislike/<slug:slug>/", views.vision_add_dislike, name="vision_add_dislike"),
    path("profile/favourites/<str:username>/", views.view_fav, name="view_fav"),
    path("profile/vision/<str:username>/", views.view_vision_created, name="view_vision_created"),
    path("profile/seed/<str:username>/", views.view_seed_created, name="view_seed_created"),
    path("profile/likes/<str:username>/", views.view_like, name="view_like"),
    path("profile/dislikes/<str:username>/", views.view_dislike, name="view_dislike"),
    path("profile/follow_user/<str:username>/", views.profile_follow_user, name="profile_follow_user"),
    path("profile/view_followed/<str:username>/", views.view_followed, name="view_followed"),
    path("profile/view_follower/<str:username>/", views.view_follower, name="view_follower"),
    path("profile/like_feedback/<int:pk>/", views.profile_like_feedback, name="profile_like_feedback"),
    path("profile/dislike_feedback/<int:pk>/", views.profile_dislike_feedback, name="profile_dislike_feedback"),
    path("profile/search_cat/", views.search_profile, name="search_profile"),
    path("profile/search_username/", views.search_username, name="search_username"),
    path("profile/return/", views.return_profile, name="return_profile"),
    path("profile/delete_user/", views.delete_user, name="delete_user"),
    path('notification/', views.notification ,name="notification")
    

]


