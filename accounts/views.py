from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .forms import UserRegistrationForm, EmployerProfileForm, ApplicantProfileForm, JobPostingForm
from .models import User, EmployerProfile, ApplicantProfile, JobPosting

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
    user_type = request.user.user_type
    
    if request.method == 'POST':
        # Initialize form with POST data
        form = EmployerProfileForm(request.POST) if user_type == 'employer' else ApplicantProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Check if profile already exists
            profile_model = EmployerProfile if user_type == 'employer' else ApplicantProfile
            profile, created = profile_model.objects.get_or_create(user=request.user)
            
            # Update profile with form data
            for field in form.fields:
                if field in request.POST:
                    setattr(profile, field, form.cleaned_data[field])
                elif field in request.FILES:
                    setattr(profile, field, request.FILES[field])
            
            profile.save()
            return redirect('employer_dashboard' if user_type == 'employer' else 'applicant_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with existing profile data if it exists
        try:
            if user_type == 'employer':
                profile = request.user.employer_profile
                form = EmployerProfileForm(instance=profile)
            else:
                profile = request.user.applicant_profile
                form = ApplicantProfileForm(instance=profile)
        except (EmployerProfile.DoesNotExist, ApplicantProfile.DoesNotExist):
            form = EmployerProfileForm() if user_type == 'employer' else ApplicantProfileForm()
    
    return render(request, 'accounts/profile_setup.html', {
        'form': form,
        'user_type': user_type
    })

@login_required
def employer_dashboard(request):
    try:
        profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        return redirect('profile_setup')
    
    # Get all active job postings for this employer
    job_postings = JobPosting.objects.filter(employer=profile).order_by('-created_at')
    
    return render(request, 'accounts/employer_dashboard.html', {
        'profile': profile,
        'job_postings': job_postings
    })

@login_required
def applicant_dashboard(request):
    try:
        profile = request.user.applicant_profile
    except ApplicantProfile.DoesNotExist:
        return redirect('profile_setup')
    return render(request, 'accounts/applicant_dashboard.html', {
        'profile': profile
    })


@login_required
def create_job_posting(request):
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'You need to complete your employer profile first.')
        return redirect('profile_setup')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.employer = employer_profile
            job_posting.save()
            messages.success(request, 'Job posting created successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobPostingForm()
    
    return render(request, 'accounts/job_posting_form.html', {
        'form': form,
        'title': 'Create Job Posting'
    })


@login_required
def edit_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    
    # Ensure the user owns this job posting
    if job_posting.employer.user != request.user:
        raise Http404("You don't have permission to edit this job posting.")
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobPostingForm(instance=job_posting)
    
    return render(request, 'accounts/job_posting_form.html', {
        'form': form,
        'title': 'Edit Job Posting'
    })


@login_required
def delete_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    
    # Ensure the user owns this job posting
    if job_posting.employer.user != request.user:
        raise Http404("You don't have permission to delete this job posting.")
    
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, 'Job posting deleted successfully!')
        return redirect('employer_dashboard')
    
    return render(request, 'accounts/confirm_delete.html', {
        'object': job_posting,
        'object_name': 'job posting',
        'cancel_url': 'employer_dashboard'
    })


@login_required
def job_detail(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, is_active=True)
    return render(request, 'accounts/job_detail.html', {
        'job': job_posting
    })
