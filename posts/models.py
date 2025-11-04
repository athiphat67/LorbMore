from django.db import models
from django.contrib.auth.models import User

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
    kind = models.CharField(max_length=100, blank=True, null=True) # เช่น "rental", "hiring"

    def __str__(self):
        # กำหนดให้ Django Admin แสดงผลด้วยฟิลด์ 'name'
        # เช่น "เครื่องใช้ไฟฟ้า", "งานฟรีแลนซ์"
        return self.name

# โมเดล Post (เป็น Concrete Base Class)
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50) # เช่น "rental" หรือ "hiring"

    skills = models.ManyToManyField(Skill, related_name='posts', blank=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)

    def __str__(self):
        # กำหนดให้ Django Admin แสดงผลด้วยฟิลด์ 'title'
        # เช่น "รับสมัครโปรแกรมเมอร์"
        return self.title

# โมเดลที่สืบทอดจาก Post
class RentalPost(Post):
    pricePerDay = models.IntegerField()
    deposit = models.IntegerField(default=0)

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # โดยใส่ "[Rental]" นำหน้า title
        # เพื่อให้แยกแยะได้ง่ายจาก HiringPost
        # เช่น "[Rental] ให้เช่ากล้อง Sony A7III"
        return f"[Rental] {self.title}"

class HiringPost(Post):
    budgetMin = models.IntegerField()
    budgetMax = models.IntegerField()
    workType = models.CharField(max_length=100) # เช่น "Full-time", "Part-time"

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # โดยใส่ "[Hiring]" นำหน้า title
        # เช่น "[Hiring] จ้างทำเว็บไซต์ E-commerce"
        return f"[Hiring] {self.title}"

# โมเดล Media ที่เชื่อมโยงกับ Post
class Media(models.Model):
    # เชื่อมโยงกับ Post ตัวหลัก
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    
    # หมายเหตุ: คุณมี 2 ฟิลด์ที่ดูเหมือนจะเก็บข้อมูลเดียวกัน (source_url และ image)
    # แนะนำให้เลือกใช้ 'image' (ImageField) เป็นหลัก และลบ 'source_url' ทิ้งครับ
    source_url = models.CharField(max_length=500) 
    image = models.ImageField(upload_to='media_images/', null=True, blank=True)

    def __str__(self):
        # กำหนดการแสดงผลในหน้า Admin
        # ถ้ามีไฟล์รูปภาพอัปโหลดอยู่ (self.image) ให้แสดงเป็น "ชื่อไฟล์"
        if self.image:
            return self.image.name
        
        # ถ้าไม่มีไฟล์ (เช่น เป็นแค่ URL หรือยังไม่ได้อัปโหลด)
        # ให้แสดงข้อความสำรองเพื่อบอกว่านี่คือ Media ของ Post ไหน
        return f"Media for Post ID: {self.post.id}"