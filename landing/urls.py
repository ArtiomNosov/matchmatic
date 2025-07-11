from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
