from django.db import models
from django.db.models import (
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    ManyToManyField,
)
from django.contrib.auth.models import User


class Topic(models.Model):
    name = CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    topic = ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)
    name = CharField(max_length=200)
    description = TextField(null=True, blank=True)
    participants = ManyToManyField(to=User, related_name="participants", blank=True)
    updated = DateTimeField(auto_now=True)
    created = DateTimeField(auto_now_add=True)

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
