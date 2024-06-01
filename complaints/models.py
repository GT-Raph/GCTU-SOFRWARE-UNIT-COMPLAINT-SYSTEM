# complaints/models.py
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
import base64
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='user_images/profile_pictures/', blank=True, null=True)
    
    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def email(self):
        return self.user.email
    # add additional fields here
    

class Category(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StudentLevel(models.Model):
    level = models.CharField(max_length=255)

    def __str__(self):
        return self.level

class StudentLevelType(models.Model):
    level_type = models.CharField(max_length=255)

    def __str__(self):
        return self.level_type

class Complaint(models.Model):
    PENDING = 'Pending'
    SOLVED = 'Solved'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SOLVED, 'Solved'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    student_level = models.ForeignKey(StudentLevel, on_delete=models.CASCADE)
    student_level_type = models.ForeignKey(StudentLevelType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    solved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    solved_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Override the groups and user_permissions fields
    groups = models.ManyToManyField(Group, blank=True, related_name='customuser_set')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='customuser_set')
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()