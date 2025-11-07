from django.contrib import admin
from .models import Post, RentalPost, HiringPost, Media, Skill, Category

# Inline class สำหรับ Media
class MediaInline(admin.TabularInline):
    model = Media
    extra = 1  # ให้มีช่องอัปโหลดว่างๆ 1 ช่องรอไว้

# Admin class สำหรับ Post ที่จะใช้ Inline
class RentalPostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]

class HiringPostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]

# ลงทะเบียนโมเดลเพื่อให้แสดงในหน้า admin
admin.site.register(RentalPost, RentalPostAdmin)
admin.site.register(HiringPost, HiringPostAdmin)
admin.site.register(Media)
admin.site.register(Skill)
admin.site.register(Category)