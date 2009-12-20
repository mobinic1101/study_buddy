from django import forms
from .models import Room
from django.contrib.auth.models import User


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["host", "participants"]
        labels = {
            "topic": "Topic:",
            "name": "Room Name:",
            "description": "Description:",
        }


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "username,email".split(',')
