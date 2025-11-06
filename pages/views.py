from django.shortcuts import render
from django.db.models import Prefetch
from posts.models import Post, HiringPost, RentalPost, Media


# ต้อง import Models จาก App ที่เก็บ Models (เปลี่ยน 'services' เป็นชื่อ App ของคุณ)
from posts.models import RentalPost, HiringPost, Media, Post 

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

def hiring_page_view(request):
    posts_with_media = Prefetch(
        'media', 
        queryset = Media.objects.all(), 
        to_attr = 'images'
    )
    
    hiring_posts = HiringPost.objects.prefetch_related(posts_with_media).order_by('-id')
    
    context = {
        "hiring_items": [_format_post_data(post) for post in hiring_posts],
    }
    return render(request, 'pages/hiring.html', context)

def rental_page_view(request):
    posts_with_media = Prefetch(
        'media', 
        queryset = Media.objects.all(), 
        to_attr = 'images'
    )
    
    rental_posts = RentalPost.objects.prefetch_related(posts_with_media).order_by('-id')
    
    context = {
        "rental_items": [_format_post_data(post) for post in rental_posts],
    }

    
    
    return render(request, 'pages/rental.html', context)

# ฟังก์ชันช่วยในการแปลงข้อมูลจาก ORM object เป็น Dict
def _format_post_data(post):
    """
    ฟังก์ชันช่วยแปลงข้อมูลจาก ORM Object -> Dict
    เพื่อส่งต่อไปยัง Template (HTML)
    """
    
    # ดึงรูปภาพแรกของโพสต์ (ถ้ามี) ตอนนี้พวกเรายังไม่มีลิ้งค์ใส่รูปภาพ
    first_image_url = None
    if hasattr(post, 'images') and post.images:
        first_media = post.images[0]
        first_image_url = (
            first_media.image.url if first_media.image
            else first_media.source_url
        )
    
    # กำหนดชื่อและราคาตามประเภทโพสต์
    price_detail = ""
    if isinstance(post, HiringPost):
        price_detail = f"เริ่มต้น {post.budgetMin:,}฿"
    elif isinstance(post, RentalPost):
        price_detail = f"เริ้มต้น {post.pricePerDay:,}฿/วัน"
    
    # ส่งค่าในรูป Dic กลับไป
    return {
        "id": post.id,
        "image_url": first_image_url or "/static/img/default.png",
        "title": post.title,
        #ตอนนี้มันยังไม่มีระบบให้คะแนน เลยสมมติค่านี้ไปก่อนนะ
        "reviews": 27 if isinstance(post, HiringPost) else 13,  
        "rating": 4.8 if isinstance(post, HiringPost) else 4.5,
        "price_detail": price_detail,
    }

def detail_post_view(request, post_id):
    
    # 1. ดึงข้อมูล Post หลัก (เอา comment ออก)
    # ใช้ get_object_or_404 จะดีกว่า .first() เพราะจะแสดง 404 Page 
    # ถ้า user ใส่ ID มั่วๆ มา
    post = get_object_or_404(
        Post.objects
        .select_related('author') # ใช้ select_related กับ ForeignKey (author)
        .prefetch_related('media', 'skills', 'categories'), # prefetch สำหรับ M2M และ Reverse FK
        pk=post_id
    )
    
    specific_post = post # เริ่มต้นให้เป็น post หลักไว้ก่อน
    if hasattr(post, 'hiringpost'):
        specific_post = post.hiringpost # ดึงข้อมูลจากตาราง hiringpost
    elif hasattr(post, 'rentalpost'):
        specific_post = post.rentalpost # ดึงข้อมูลจากตาราง rentalpost
    
    context = {
        'post': specific_post,      # ตัวนี้จะมี field pricePerDay หรือ budgetMin
        'media': post.media.all(),  # media ยังคงดึงจาก post หลัก
    }
    
    return render(request, 'pages/detail_post.html', context) 

