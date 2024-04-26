from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .forms import RoomForm
from .models import Room, Topic, User, Message


def register_user(request):
    register_form = UserCreationForm()
    context = {"title": "Register User", "register_form": register_form}

    if request.method == "POST":
        register_form = UserCreationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        messages.error(request, "an error ocurred during processing the form.")

    return render(request, "first_app/login_register_form.html", context)


def login_user(request):
    context = {"title": "Login"}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        context["username"] = username
        context["password"] = password

        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user != None:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect("home")
            messages.error(request, "Password is incorrect.")
        else:
            messages.error(request, "a user with this username dose'nt exist.")

    return render(request, "first_app/login_register_form.html", context)


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect(to="home")
    return redirect(to="home")


def home(request):
    q = request.GET.get("q")

    topics = Topic.objects.all()
    rooms = (
        Room.objects.filter(
            Q(topic__name__icontains=q)
            | Q(name__icontains=q)
            | Q(host__username__icontains=q)
        )
        if q
        else Room.objects.all()
    )
    rooms_count = rooms.count()

    context = {
        "rooms": rooms.order_by("-created", "-updated"),
        "topics": topics,
        "rooms_count": rooms_count,
    }

    if request.user.is_authenticated:
        user_participated_rooms = request.user.participants.all().values_list(
            "id", flat=True
        )
        room_messages = []
        for room_id in user_participated_rooms:
            room_messages.append(Message.objects.filter(room__id=room_id).first())
        room_messages.sort(key=lambda message: message.id, reverse=True)

        context["room_messages"] = room_messages

    return render(request, "first_app/home.html", context)


def room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    comments = Message.objects.filter(room__id=primary_key).order_by("-created")

    if request.method == "POST":
        body = request.POST.get("body")
        Message.objects.create(user=request.user, room=room, body=body)
        if not room.participants.filter(id=request.user.id).exists():
            room.participants.add(request.user)
        return redirect("room", primary_key=primary_key)

    participants = room.participants.all()
    data = {"room": room, "comments": comments, "participants": participants}
    return render(request, "first_app/room.html", data)


@login_required(login_url="/login")
def create_room(request):
    form_to_render = RoomForm()
    if request.method == "POST":
        form = RoomForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "first_app/room_form.html", {"form": form_to_render.as_p()})


@login_required(login_url="/login")
def update_room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    if request.user.username != room.host.username:  # type: ignore
        return HttpResponse("You are not allowed to be there!!!")
    form_to_render = RoomForm(instance=room)
    if request.method == "POST":
        form = RoomForm(data=request.POST, instance=room)
        if form.is_valid():
            form.save()
            print("form is valid")
            return redirect("home")
    return render(request, "first_app/room_form.html", {"form": form_to_render.as_p()})


@login_required(login_url="/login")
def delete_room(request, primary_key):
    room = Room.objects.filter(id=primary_key)

    if not room.exists():
        return HttpResponse("Page not found")

    room = room[0]
    if request.user.username != room.host.username:  # type: ignore
        return HttpResponse("You are not allowed to be there!!!")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "first_app/delete.html", {"object": room})


@login_required(login_url="/login")
def delete_message(request, primary_key):
    primary_key = int(primary_key)
    message = Message.objects.filter(id=primary_key)

    if not message.exists():
        return HttpResponse("Page not found")

    message = message[0]
    if request.user.username == message.user.username:
        if request.method == "POST":
            message.delete()
            return redirect(to="room", primary_key=message.room.id)  # type: ignore
    else:
        return HttpResponse(
            "You are not allowed to be here. <p>Probably because you are not the owner of this message you want to delete."
        )

    context = {"object": message}
    return render(request, "first_app/delete.html", context)
