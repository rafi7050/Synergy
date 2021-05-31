from django.urls import path
from knowledge import views

# name of the app when calling it externally
app_name = "knowledge"

urlpatterns = [
    path("seed/create/", views.seed_create, name="seed_create"),
    path("seed/link/<slug:slug>/", views.one_seed, name="one_seed"),
    path("seed/edit/<slug:slug>/", views.seed_edit, name="seed_edit"),
    path("seed/delete_comment/<int:pk>/", views.seed_delete_comment, name="seed_delete_comment"),
    path("seed/comment_add_like/<int:pk>/", views.comment_add_like, name="comment_add_like"),
    path("seed/comment_add_dislike/<int:pk>/", views.comment_add_dislike, name="comment_add_dislike"),
    path("seed/add_doc/<slug:slug>/", views.seed_add_doc, name="seed_add_doc"),
    path("seed/delete_doc/<int:pk>/", views.seed_delete_doc, name="seed_delete_doc"),
    path("seed/delete/<slug:slug>/", views.seed_delete, name="seed_delete"),
    path("seed/search/", views.search_seed, name="search_seed"),
    path("seed/keywords_view/", views.search_keywords_view, name="search_keywords_view"),
    path("seed/return/", views.return_seed, name="return_seed"),
    path("vision/create/", views.vision_create, name="vision_create"),
]