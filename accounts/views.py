from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, EmployerProfileForm, ApplicantProfileForm
from .models import User

def register(request, role):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = role
            user.save()
            login(request, user)
            return redirect('profile_setup')
    else:
        form = UserRegistrationForm(initial={'user_type': role})
    return render(request, 'accounts/register.html', {'form': form, 'role': role})

@login_required
def profile_setup(request):
    if request.user.user_type == 'employer':
        ProfileForm = EmployerProfileForm
        template = 'accounts/employer_profile.html'
    else:
        ProfileForm = ApplicantProfileForm
        template = 'accounts/applicant_profile.html'
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = ProfileForm()
    
    return render(request, template, {'form': form})
