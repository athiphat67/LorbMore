from django.db import models
from django.contrib.auth.models import User

# โมเดลหลักที่ Post จะอ้างอิงถึง
class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=100, blank=True, null=True) # เช่น "rental", "hiring"

    def __str__(self):
        return self.name

# โมเดล Post (เป็น Concrete Base Class)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50) # เช่น "rental" หรือ "hiring"

    # ความสัมพันธ์ Many-to-Many (แทนตาราง PostSkill และ PostCategory)
    # Django จะสร้างตาราง join ให้เราอัตโนมัติ
    skills = models.ManyToManyField(Skill, related_name='posts', blank=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)

    def __str__(self):
        return self.title

# โมเดลที่สืบทอดจาก Post
class RentalPost(Post):
    pricePerDay = models.IntegerField()
    deposit = models.IntegerField(default=0)

    def __str__(self):
        return f"[Rental] {self.title}"

class HiringPost(Post):
    budgetMin = models.IntegerField()
    # สังเกตว่าใน UML เขียนว่า buggetMax, ผมแก้เป็น budgetMax นะครับ
    budgetMax = models.IntegerField()
    workType = models.CharField(max_length=100) # เช่น "Full-time", "Part-time"

    def __str__(self):
        return f"[Hiring] {self.title}"

# โมเดล Media ที่เชื่อมโยงกับ Post
class Media(models.Model):
    # เชื่อมโยงกับ Post ตัวหลัก
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    source_url = models.CharField(max_length=500) 
    image = models.ImageField(upload_to='media_images/', null=True, blank=True)

    def __str__(self):
        if self.image:
            return self.image.name
        return f"Media for Post ID: {self.post.id}"