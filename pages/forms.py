from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        label="อีเมล (ใช้อีเมล @dome.tu.ac.th เพื่อรับสิทธิ์สร้างงาน)",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        # เช็คว่าเป็นอีเมลมหาวิทยาลัยหรือไม่
        if email.endswith('@dome.tu.ac.th'):
            local_part = email.split('@')[0]

            if '.' not in local_part:
                raise forms.ValidationError("รูปแบบอีเมลไม่ถูกต้อง (ต้องมีจุด . คั่น)")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้งานไปแล้ว")

        return email
    
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Email Address')
    subject = forms.CharField(max_length=200, label='Subject')
    message = forms.CharField(widget=forms.Textarea, label='Message')