# ใน posts/forms.py

from django import forms
from .models import HiringPost, RentalPost


# ----- 1. นี่คือคลาส Widget ที่แก้ไขใหม่ -----
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        # 1. เรียกคลาสแม่ให้ทำงานให้เสร็จก่อน
        #    โดยส่ง attrs ปกติ (ที่ไม่มี multiple) เข้าไป
        super().__init__(attrs)
        
        # 2. "หลังจาก" ที่คลาสแม่ทำงาน (และตรวจสอบ) เสร็จแล้ว
        #    เราค่อยเพิ่ม 'multiple' = True เข้าไปใน attribute ของ widget
        #    เพื่อบังคับให้ HTML ที่ render ออกมามีคำว่า multiple
        self.attrs['multiple'] = True

# ----------------------------------------


class HiringPostForm(forms.ModelForm):
    images = forms.FileField(
        # 2. ใช้งาน Widget ที่แก้ไขใหม่
        widget=MultipleFileInput(), 
        required=False, 
        label="อัปโหลดรูปภาพ (เลือกหลายรูปได้)"
    )

    class Meta:
        model = HiringPost
        fields = [
            "title",
            "description",
            "categories",
            "skills",
            "budgetMin",
            "budgetMax",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class RentalPostForm(forms.ModelForm):
    images = forms.FileField(
        # 3. ใช้งาน Widget ที่แก้ไขใหม่
        widget=MultipleFileInput(), 
        required=False, 
        label="อัปโหลดรูปภาพ (เลือกหลายรูปได้)"
    )

    class Meta:
        model = RentalPost
        fields = ["title", "description", "categories", "pricePerDay", "deposit"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }