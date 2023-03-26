from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, Profile
from .forms import RoomForm, UserForm


# Create your views here.


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)

        except:
            messages.error(request, "User doesn't exist.")

        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password doesn't exist.")

    page = 'login'
    context = {
        'page': page
    }

    return render(request, 'base/login_register.html', context)


def registerPage(request):

    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user_profile = Profile(user=user)
            user_profile.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, 'Something went wrong while registering a user')
    context = {

        'form': form
    }
    return render(request, 'base/login_register.html', context)


@login_required(login_url="login")
def updateUser(request):
    # No need for the id because the user will be the
    # logged in user
    user = request.user
    # form = UserForm(instance=user)

    if request.method == "POST":

        data = request.POST
        user_profile = Profile.objects.get(user=user)
        user.username = data['username']
        user.email = data['email']
        if request.FILES:
            user_profile.image = request.FILES['avatar']
        user_profile.bio = data['user_bio']
        user.save()
        user_profile.save()
        return redirect('user', pk=user.id)

    context = {}
    return render(request, 'base/edit-user.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
    }
    return render(request, 'base/profile.html', context)


def home(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {
        'room_count': room_count,
        "topics": topics,
        "rooms": rooms,
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', context)


def room(request, pk):

    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    if request.method == "POST":
        messages = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('comment')
        )
        return redirect('room', pk=room.id)
    context = {
        'room_messages': room_messages,
        'room': room,
        'participants': participants
    }
    return render(request, 'base/room.html', context)


def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('you arenot allowed here!!')

    message.delete()
    return redirect('home')


@login_required(login_url="login")
def createRoom(request):

    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form,
               'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    room_topic = room.topic

    if request.user != room.host:
        return HttpResponse('you ar enot allowed here!!')

    if request.method == 'POST':

        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')

        room.save()
        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
        'room_topic': room_topic
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('you ar enot allowed here!!')

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {"obj": room})


def topicsPage(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(
        Q(name__icontains=q)
    )

    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.filter(

    )
    context = {"room_messages": room_messages}
    return render(request, 'base/activity.html', context)
