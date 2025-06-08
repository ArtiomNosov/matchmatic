from django.urls import path
from . import views

urlpatterns = [
    path('register/<str:role>/', views.register, name='register'),
    path('profile/', views.profile_setup, name='profile_setup'),
]
