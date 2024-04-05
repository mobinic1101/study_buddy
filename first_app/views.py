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
    return render(
        request,
        "first_app/home.html",
        {
            "rooms": rooms.order_by("-created", "-updated"),
            "topics": topics,
            "rooms_count": rooms_count,
        },
    )


def room(request, primary_key):
    room = Room.objects.get(id=primary_key)
    comments = Message.objects.filter(room__id=primary_key).order_by("-created")
    data = {"room": room, "comments": comments}

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
    room = Room.objects.get(id=primary_key)
    if request.user.username != room.host.username:  # type: ignore
        return HttpResponse("You are not allowed to be there!!!")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "first_app/delete.html", {"object": room})
