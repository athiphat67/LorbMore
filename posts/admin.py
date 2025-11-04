from django.contrib import admin
from .models import Post, RentalPost, HiringPost, Media, Skill, Category

# ลงทะเบียนโมเดลเพื่อให้แสดงในหน้า admin
admin.site.register(RentalPost)
admin.site.register(HiringPost)
admin.site.register(Media)
admin.site.register(Skill)
admin.site.register(Category)