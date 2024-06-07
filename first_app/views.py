from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
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
    q = "" if not q else q
    print(q)

    topics = Topic.objects.all()
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(host__username__icontains=q)
    )
    rooms_count = rooms.count()
    rooms_count_all = Room.objects.all().count()
    url = reverse("home")

    context = {
        "view_name": home.__name__,
        "rooms": rooms.order_by("-created", "-updated"),
        "topics": topics,
        "rooms_count": rooms_count,
        "rooms_count_all": rooms_count_all,
        "url": url,
    }

    if request.user.is_authenticated:
        user_participated_rooms = request.user.participants.filter(
            Q(name__icontains=q) | Q(topic__name__icontains=q)
        ).values_list("id", flat=True)
        room_messages = Message.objects.filter(room__id__in=user_participated_rooms)
        # type: ignore
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
    topics = Topic.objects.all()

    form_to_render = RoomForm()
    if request.method == "POST":
        topic, _ = Topic.objects.get_or_create(name=request.POST.get("topic"))

        room = Room(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        room.save()

        return redirect("home")

    context = {"template_name": "Create", "form": form_to_render, "topics": topics}
    return render(request, "first_app/room_form.html", context)


@login_required(login_url="/login")
def update_room(request, primary_key):
    room = Room.objects.get(id=primary_key)

    # security check
    if request.user.username != room.host.username:  # type: ignore
        return HttpResponse("You are not allowed to be there!!!")

    form_to_render = RoomForm(instance=room)
    if request.method == "POST":
        topic, _ = Topic.objects.get_or_create(name=request.POST.get("topic"))

        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")

        room.save()

        return redirect("home")

    context = {"form": form_to_render, "template_name": "Update", "topic": room.topic}
    return render(request, "first_app/room_form.html", context)


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
            return redirect(to="home")  # type: ignore
    else:
        return HttpResponse(
            "You are not allowed to be here. <p>Probably because you are not the owner of this message you want to delete."
        )

    context = {"object": message}
    return render(request, "first_app/delete.html", context)


def user_profile(request, primary_key):
    def get_topics(rooms):
        """
        rooms: QuerySet | a list of room objects\n
        extracts all of the topics exist in the rooms\n
        -> tuple([topic, topic, ...], {topic: n, topic: n, ...})
        """
        topics = []
        topics_count = {}
        for room in rooms:
            topic = room.topic
            if topic not in topics:
                topics.append(topic)
                topics_count[topic.name] = 1
            else:
                topics_count[topic.name] += 1
        return topics, topics_count

    user = User.objects.get(id=primary_key)

    # a quick security check!
    if request.user.id == user.id:  # type: ignore
        if not request.user.is_authenticated:
            return redirect(to="login")

    q = request.GET.get("q")
    all_rooms = Room.objects.filter(host__id=primary_key)

    rooms = (
        all_rooms
        if not q
        else Room.objects.filter(
            Q(host__id=primary_key) & Q(topic__name__icontains=q) | Q(name__icontains=q)
        )
    )
    topics, topics_count = get_topics(all_rooms)
    room_messages = Message.objects.filter(user__id=primary_key)
    url = reverse("user_profile", args=primary_key)
    print(topics_count)

    context = {
        "view_name": user_profile.__name__,
        "user": user,
        "rooms": rooms,
        "topics": topics,
        "topics_count": topics_count,
        "room_messages": room_messages,
        "rooms_count_all": all_rooms.count(),
        "url": url,
    }
    return render(request, "first_app/user_profile.html", context)
