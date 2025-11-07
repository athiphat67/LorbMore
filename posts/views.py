from django.shortcuts import render
from .models import Post, HiringPost, RentalPost, Media
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.core.paginator import Paginator

# Create your views here.
def hiring_page_view(request):
    posts_with_media = Prefetch(
        'media', 
        queryset = Media.objects.all(), 
        to_attr = 'images'
    )
    
    # ดึง "QuerySet" ทั้งหมดมา 
    all_hiring_posts = HiringPost.objects.prefetch_related(posts_with_media).order_by('-id')
    
    # สร้าง Paginator (ตั้งค่า 6 โพสต์ต่อหน้า)
    paginator = Paginator(all_hiring_posts, 6) 
    
    # ดึงเลขหน้าจาก URL 
    page_number = request.GET.get('page')
    
    # ดึงข้อมูล "หน้า" ที่ถูกต้องมา
    page_obj = paginator.get_page(page_number)
    formatted_items = [_format_post_data(post) for post in page_obj]

    context = {
        "hiring_items": formatted_items, 
        "page_obj": page_obj              # ส่ง 'page_obj' ไปให้ Template
    }
    return render(request, 'pages/hiring.html', context)

def rental_page_view(request):
    posts_with_media = Prefetch(
        'media', 
        queryset = Media.objects.all(), 
        to_attr = 'images'
    )
    
    # ดึง "QuerySet" ทั้งหมดมา
    all_rental_posts = RentalPost.objects.prefetch_related(posts_with_media).order_by('-id')
    
    # สร้าง Paginator (6 โพสต์ต่อหน้า)
    paginator = Paginator(all_rental_posts, 6) 
    
    # ดึงเลขหน้าจาก URL
    page_number = request.GET.get('page')
    
    # ดึงข้อมูล "หน้า" ที่ถูกต้องมา
    page_obj = paginator.get_page(page_number)
    formatted_items = [_format_post_data(post) for post in page_obj]
    
    context = {
        "rental_items": formatted_items,  
        "page_obj": page_obj              # ส่ง 'page_obj' ไปให้ Template
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
    
    # ดึงข้อมูล Post หลัก 
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
        'post': specific_post,      
        'media': post.media.all(),  
        'skills': post.skills.all(),     
        'categories': post.categories.all() 
    }
    
    return render(request, 'pages/detail_post.html', context) 


