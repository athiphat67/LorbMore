from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'displayName', 'studentId', 'show_image')
    list_display_links = ('user', 'displayName')
    readonly_fields = ('show_image',)

    def show_image(self, obj):
        if obj.profile_image:
            # แสดงรูปขนาดความสูงไม่เกิน 100px
            return format_html('<img src="{}" style="max-height: 100px; border-radius: 5px;" />', obj.profile_image.url)
        return "-"
    
    show_image.short_description = 'รูปโปรไฟล์ปัจจุบัน' 

admin.site.register(Profile, ProfileAdmin)