from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import subprocess

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'signup.html', {'error': 'Username and password are required'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            import sys
            import os
            subprocess.Popen([sys.executable, os.path.join(os.getcwd(), 'gui_player.py'), username])

            return redirect('login')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')
