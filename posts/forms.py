# ใน posts/forms.py

from django import forms
from .models import HiringPost, RentalPost, Category


class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):

        super().__init__(attrs)

        self.attrs["multiple"] = True


class HiringPostForm(forms.ModelForm):
    images = forms.FileField(
        # 2. ใช้งาน Widget ที่แก้ไขใหม่
        widget=MultipleFileInput(),
        required=False,
        label="อัปโหลดรูปภาพ (เลือกหลายรูปได้)",
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # กรอง 'categories' ให้แสดงเฉพาะหมวดหมู่ที่เป็น is_hiring_category = True
        self.fields['categories'].queryset = Category.objects.filter(is_hiring_category=True)

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
        label="อัปโหลดรูปภาพ (เลือกหลายรูปได้)",
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # กรอง 'categories' ให้แสดงเฉพาะหมวดหมู่ที่เป็น is_rental_category = True
        self.fields['categories'].queryset = Category.objects.filter(is_rental_category=True)

    class Meta:
        model = RentalPost
        fields = ["title", "description", "categories", "pricePerDay", "deposit"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
