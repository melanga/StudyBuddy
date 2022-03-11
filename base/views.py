from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic
from .forms import RoomForm


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Enter correct username or password")

    context = {}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def home(request):
    # get q value in url to filter out the topic
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    selected_room = Room.objects.get(id=pk)
    context = {'room': selected_room}
    return render(request, 'base/room.html', context)


# if user is not logged in, user is redirected to login page when create room request
@login_required(login_url='login')
def create_room(request):
    form = RoomForm
    # POST method is defined in room_form.html as form submission and http request come from same address as from url,
    # so we need to check if it is form submission or page request and is it is a POST request from form,
    # we need to handle it instead of rendering the html content.
    if request.method == "POST":
        # to access data and manually validate if you want
        # request.POST.get('name')
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    # get room object data from id
    selected_room = Room.objects.get(id=pk)
    # pre-fill the form using room data
    form = RoomForm(instance=selected_room)

    if request.user != selected_room.host:
        return HttpResponse('Only host can edit room attributes...')

    if request.method == "POST":
        # instance is defined to update the existing data instead of creating new one
        form = RoomForm(request.POST, instance=selected_room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    selected_room = Room.objects.get(id=pk)

    if request.user != selected_room.host:
        return HttpResponse('Only host can edit room attributes...')

    if request.method == "POST":
        selected_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': selected_room})
