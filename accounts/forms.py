from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployerProfile, ApplicantProfile

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'website', 'industry', 'description')

class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ('resume', 'skills', 'experience', 'education')
