from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views import View

# Create your views here.

class LandingPageView(View):
    def get(self, request):
        return render(request, 'landing/index.html')

class SignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('landing:landing')
        form = UserCreationForm()
        return render(request, 'landing/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing:landing')
        return render(request, 'landing/signup.html', {'form': form})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('landing:landing')
        form = AuthenticationForm()
        return render(request, 'landing/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('landing:landing')
        return render(request, 'landing/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing:landing')
