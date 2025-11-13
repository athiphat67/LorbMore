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
        labels = {
            "title": "ชื่อโพสต์",
            "description" : "รายละเอียด",
            "categories": "เลือกหมวดหมู่(ประเภท)บริการของคุณ",
            "skills": "เลือกทักษะการบริการของคุณ",
            "budgetMin": "งบประมาณ (ต่ำสุด)",
            "budgetMax": "งบประมาณ (สูงสุด)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "categories": forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
            "skills": forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
            "budgetMin": forms.NumberInput(attrs={"class": "form-control"}),
            "budgetMax": forms.NumberInput(attrs={"class": "form-control"}),
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
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "categories": forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
            "pricePerDay": forms.NumberInput(attrs={"class": "form-control"}),
            "deposit": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "ชื่อโพสต์",
            "description" : "รายละเอียด",
            "categories": "เลือกหมวดหมู่(ประเภท)สินค้าของคุณ",
            "pricePerDay": "ราคาเช่าต่อวัน/ครั้ง",
            "deposit": "ราคามัดจำการเช่า",
        }
