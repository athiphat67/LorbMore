from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

# โมเดลหลักที่ Post จะอ้างอิงถึง
class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        # เมธอดนี้กำหนดให้ Django Admin แสดงผล object นี้
        # ด้วยค่าจากฟิลด์ 'name'
        # เช่น แสดงเป็น "Programming" หรือ "Design"
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    
    is_hiring_category = models.BooleanField(
        "hiring", 
        default=True
    )
    
    # เปลี่ยนป้ายกำกับ และลบ help_text
    is_rental_category = models.BooleanField(
        "rental", 
        default=True
    )

    def __str__(self):
        # กำหนดให้ Django Admin แสดงผลด้วยฟิลด์ 'name'
        # เช่น "เครื่องใช้ไฟฟ้า", "งานฟรีแลนซ์"
        return self.name


# โมเดล Post (เป็น Concrete Base Class)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    POST_TYPE_CHOICES = [
        ('rental', 'Rental Post'),
        ('hiring', 'Hiring Post'),
    ]
    type = models.CharField(
        max_length=50, choices=POST_TYPE_CHOICES, editable=False, null=True
    )

    categories = models.ManyToManyField(Category, related_name="posts", blank=True)
    bookings = models.ManyToManyField(User, related_name='booked_posts', blank=True)

    def __str__(self):
        # กำหนดให้ Django Admin แสดงผลด้วยฟิลด์ 'title'
        # เช่น "รับสมัครโปรแกรมเมอร์"
        return self.title

    @property
    def avg_rating(self):
        # คำนวณค่าเฉลี่ยจาก field 'rating' ของ model Review ที่ผูกกับโพสต์นี้
        # โดยสมมติว่าใน Review model ใช้ related_name='reviews'
        ratings = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return ratings if ratings else 0

    @property
    def count_reviews(self):
        return self.reviews.count()


# โมเดลที่สืบทอดจาก Post
class RentalPost(Post):
    pricePerDay = models.IntegerField()
    deposit = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        self.type = 'rental' 
        super().save(*args, **kwargs)

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # โดยใส่ "[Rental]" นำหน้า title
        # เพื่อให้แยกแยะได้ง่ายจาก HiringPost
        # เช่น "[Rental] ให้เช่ากล้อง Sony A7III"
        return f"[Rental] {self.title}"


class HiringPost(Post):
    budgetMin = models.IntegerField()
    budgetMax = models.IntegerField()
    skills = models.ManyToManyField(Skill, related_name="hiring_posts", blank=True)
    
    def save(self, *args, **kwargs):
        self.type = 'hiring'
        super().save(*args, **kwargs) 

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # โดยใส่ "[Hiring]" นำหน้า title
        # เช่น "[Hiring] จ้างทำเว็บไซต์ E-commerce"
        return f"[Hiring] {self.title}"


# โมเดล Media ที่เชื่อมโยงกับ Post
class Media(models.Model):
    # เชื่อมโยงกับ Post ตัวหลัก
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    image = models.ImageField(upload_to="media_images/", null=True, blank=True)

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # ถ้ามีไฟล์รูปภาพอัปโหลดอยู่ (self.image) ให้แสดงเป็น "ชื่อไฟล์"
        if self.image:
            return self.image.name

        # ถ้าไม่มีไฟล์ (เช่น เป็นแค่ URL หรือยังไม่ได้อัปโหลด)
        # ให้แสดงข้อความสำรองเพื่อบอกว่านี่คือ Media ของ Post ไหน
        return f"Media for Post ID: {self.post.id}"


class Review(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        help_text="คะแนน 1-5 ดาว"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'author') # ป้องกันคนเดิมรีวิวโพสต์เดิมซ้ำ

    def __str__(self):
        return f"Rating {self.rating} on {self.post.title} by {self.author.username}"