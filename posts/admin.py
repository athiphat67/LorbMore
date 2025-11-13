from django.contrib import admin
from .models import Post, RentalPost, HiringPost, Media, Skill, Category


# Inline class สำหรับ Media
class MediaInline(admin.TabularInline):
    model = Media
    extra = 1


# Admin class สำหรับ Post ที่จะใช้ Inline
class RentalPostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    filter_horizontal = ("categories",)


class HiringPostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    filter_horizontal = (
        "categories",
        "skills",
    )


# ลงทะเบียนโมเดลเพื่อให้แสดงในหน้า admin
admin.site.register(RentalPost, RentalPostAdmin)
admin.site.register(HiringPost, HiringPostAdmin)
admin.site.register(Media)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("name", "is_hiring_category", "is_rental_category")

    search_fields = ("name",)

    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "ประเภทการใช้งาน",
            {
                "fields": ("is_hiring_category", "is_rental_category"),
                "description": "เลือกประเภทโพสต์ที่หมวดหมู่นี้จะปรากฏ (สามารถเลือกได้ทั้งคู่)",
            },
        ),
    )
