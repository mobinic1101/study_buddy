from django.db import models
from django.db.models import (
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    ManyToManyField,
    ImageField,
    OneToOneField
)
from django.contrib.auth.models import User
from django.conf.global_settings import MEDIA_ROOT

import os


class Topic(models.Model):
    name = CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = ForeignKey(to=User, on_delete=models.SET_NULL, null=True)  # type: ignore
    topic = ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)
    name = CharField(max_length=200)
    description = TextField(null=True, blank=True)
    participants = ManyToManyField(to=User, related_name="participants", blank=True)
    updated = DateTimeField(auto_now=True)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-updated"]

    def __str__(self):
        return self.name


class Message(models.Model):
    user = ForeignKey(to=User, on_delete=models.CASCADE)
    room = ForeignKey(to=Room, on_delete=models.CASCADE)
    body = TextField()
    updated = DateTimeField(auto_now=True)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]

    class Meta:
        ordering = ["-created", "-updated"]

    
class UserProfile(models.Model):
    user = OneToOneField(to=User, on_delete=models.CASCADE, related_name="user_profile")
    image = ImageField(
        upload_to="profile_pics/", default=os.path.join(MEDIA_ROOT, "profile_pics", "avatar.svg"))

    @property
    def get_image_url(self):
        # if there is no profile image we use the default one.
        url = self.image.url
        print("ImageUrl: ", url)
        if self.image.url:
            return url
        