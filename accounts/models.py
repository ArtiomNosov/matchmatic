from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPES = (
        ('employer', 'Employer'),
        ('applicant', 'Applicant'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='applicant')
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class EmployerProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.company_name

class ApplicantProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='applicant_profile')
    resume = models.FileField(upload_to='resumes/', blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username
