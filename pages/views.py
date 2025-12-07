from django.shortcuts import render, redirect
from django.db.models import Prefetch
from posts.models import Post, HiringPost, RentalPost, Media
from posts.views import _format_post_data
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import StudentRegisterForm

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