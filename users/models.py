from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    studentId = models.CharField(max_length=10, blank=True, null=True)
    displayName = models.CharField(max_length=255)
    bioSkills = models.TextField(blank=True, null=True)
    socialMedia = models.CharField(max_length=255, blank=True, null=True)
    phoneNum = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username