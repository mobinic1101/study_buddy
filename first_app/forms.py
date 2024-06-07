from django import forms
from .models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ["host", "participants"]
        labels = {
            "topic": "Topic:",
            "name": "Room Name:",
            "description": "Description:"
        }

