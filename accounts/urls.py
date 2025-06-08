from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Authentication and Profile
    path('register/<str:role>/', views.register, name='register'),
    path('profile/', views.profile_setup, name='profile_setup'),
    
    # Dashboards
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    
    # Job Postings
    path('job/new/', login_required(views.create_job_posting), name='create_job_posting'),
    path('job/<int:pk>/', login_required(views.job_detail), name='job_detail'),
    path('job/<int:pk>/edit/', login_required(views.edit_job_posting), name='edit_job_posting'),
    path('job/<int:pk>/delete/', login_required(views.delete_job_posting), name='delete_job_posting'),
]
