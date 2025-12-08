from django import forms
from django.contrib.auth.models import User
from .models import Profile

# ฟอร์มแก้ไขข้อมูลบัญชี (User Model)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, label="ชื่อจริง")
    last_name = forms.CharField(max_length=30, required=False, label="นามสกุล")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

# ฟอร์มแก้ไขข้อมูลโปรไฟล์ (Profile Model)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['displayName', 'studentId', 'bioSkills', 'phoneNum', 'socialMedia']
        labels = {
            'displayName': 'ชื่อที่ใช้แสดง (Display Name)',
            'studentId': 'รหัสนักศึกษา',
            'bioSkills': 'ทักษะ / แนะนำตัว',
            'phoneNum': 'เบอร์โทรศัพท์',
            'socialMedia': 'Social Media / ช่องทางติดต่อ',
        }
        widgets = {
            'bioSkills': forms.Textarea(attrs={'rows': 3}),
        }