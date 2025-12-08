from django.shortcuts import render, redirect
from django.db.models import Prefetch
from posts.models import Post, HiringPost, RentalPost, Media
from posts.views import _format_post_data
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import StudentRegisterForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def about_page_view(request):
    return render(request, 'pages/about.html')

def home_page_view(request):

    posts_with_media = Prefetch(
        'media', 
        queryset=Media.objects.all(), 
        to_attr='images'
    )
    
    # ดึงข้อมูล 3 โพสต์ล่าสุดของแต่ละประเภท
    latest_hiring = HiringPost.objects.prefetch_related(posts_with_media).order_by('-id')[:3]
    latest_rental = RentalPost.objects.prefetch_related(posts_with_media).order_by('-id')[:3]
    
    #  context เพื่อส่งไปให้ HTML
    context = {
        # แปลงข้อมูลโดยใช้ฟังก์ชัน _format_post_data ของคุณเอง
        "hiring_items": [_format_post_data(post) for post in latest_hiring],
        "rental_items": [_format_post_data(post) for post in latest_rental],
    }
    
    return render(request, 'pages/home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentRegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # --- ตรงนี้คือจุดที่เอาข้อมูลไปใช้งาน ---
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # วิธีที่ 1 (ง่ายสุด): ปริ้นท์ลง Terminal เพื่อเช็คว่าข้อมูลเข้าไหม
            print(f"New Message from {name} ({email}): {message}")
            
            # วิธีที่ 2 (ส่งอีเมลจริง): ต้องตั้งค่า Email ใน settings.py ก่อน
            # send_mail(
            #     subject=f"New Contact from {name}",
            #     message=message,
            #     from_email=email,
            #     recipient_list=['your_admin_email@example.com'],
            # )

            messages.success(request, 'Message sent successfully! We will get back to you soon.')
            return redirect('contact') # redirect กลับมาหน้าเดิม
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})