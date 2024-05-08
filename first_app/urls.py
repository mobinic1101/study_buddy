from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("", views.home, name="home"),
    path("room/<str:primary_key>", views.room, name="room"),
    path("create_room/", views.create_room, name="create_room"),
    path("update_room/<str:primary_key>", views.update_room, name="update_room"),
    path("delete_room/<str:primary_key>", views.delete_room, name="delete_room"),
    path(
        "delete_message/<str:primary_key>", views.delete_message, name="delete_message"
    ),
    path("user_profile/<str:primary_key>", views.user_profile, name="user_profile"),
]
