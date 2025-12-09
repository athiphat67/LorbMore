from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# Create your models here.
class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    studentId = models.CharField(max_length=10, blank=True, null=True)
    displayName = models.CharField(max_length=255)
    bioSkills = models.TextField(blank=True, null=True)
    socialMedia = models.CharField(max_length=255, blank=True, null=True)
    phoneNum = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    def get_average_rating(self):
        # 1. เข้าถึง User -> ไปหา Post ทั้งหมดของ User นี้
        # 2. จาก Post ทั้งหมด -> ไปหา Review ทั้งหมด
        # 3. หาค่าเฉลี่ย (Avg) ของ field 'rating'
        
        reviews_avg = self.user.posts.aggregate(avg_score=Avg('reviews__rating'))
        
        score = reviews_avg['avg_score']
        if score:
            return round(score, 1) # ทศนิยม 1 ตำแหน่ง เช่น 4.5
        return 0 # ถ้ายังไม่มีรีวิวเลย