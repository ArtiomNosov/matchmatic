from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployerProfile, ApplicantProfile, JobPosting

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class EmployerProfileForm(forms.ModelForm):
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        error_messages={'invalid': 'Enter a valid URL (e.g., https://example.com)'}
    )
    
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'website', 'industry', 'description', 'location')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'})
        }

class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ('resume', 'skills', 'experience', 'education')


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ('title', 'description', 'requirements', 'location', 'employment_type', 'salary')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.TextInput(attrs={'class': 'form-control'}),
        }
