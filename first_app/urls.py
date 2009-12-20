from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("", views.home, name="home"),
    path("room/<str:primary_key>", views.room, name="room"),
    path("create-room/", views.create_room, name="create_room"),
    path("update-room/<str:primary_key>", views.update_room, name="update_room"),
    path("delete-room/<str:primary_key>", views.delete_room, name="delete_room"),
    path(
        "delete-message/<str:primary_key>", views.delete_message, name="delete_message"
    ),
    path("user-profile/<str:primary_key>", views.user_profile, name="user_profile"),
    path("update-user", views.update_user, name="update_user"),
]

if settings.DEBUG:
    urlpatterns += static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
