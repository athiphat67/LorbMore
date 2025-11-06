from django.shortcuts import render
from django.db.models import Prefetch
from posts.models import Post, HiringPost, RentalPost, Media

# Create your views here.
def about_page_view(request):
    return render(request, 'pages/about.html')

def home_page_view(request):
    return render(request, 'pages/home.html')

def hiring_page_view(request):
    return render(request, 'pages/hiring.html')

def rental_page_view(request):
    return render(request, 'pages/rental.html')

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

# --- Views Functions ---
def home_page_view(request):
    
    # ใช้ Prefetch เพื่อดึง media ของโพสต์แต่ละรายการใน query เดียว
    posts_with_media = Prefetch(
        'media', 
        queryset = Media.objects.all(), 
        to_attr = 'images'
    )
    
    # ดึง Hiring Posts (ล่าสุด 3 โพสต์) ตอนนี้ยังไม่มีคะแนน
    hiring_posts = HiringPost.objects.prefetch_related(posts_with_media).order_by('-id')[:3]
    rental_posts = RentalPost.objects.prefetch_related(posts_with_media).order_by('-id')[:3]

    context = {
        "hiring_items": [_format_post_data(post) for post in hiring_posts],
        "item_rental_items": [_format_post_data(post) for post in rental_posts],
    }
    
    return render(request, 'pages/home.html', context) 

def detail_post_view(request, post_id):
    
    # Logic เพื่อดึงข้อมูลเฉพาะจากโมเดลลูก
    if hasattr(post, 'hiringpost'):
        specific_post = post.hiringpost
    elif hasattr(post, 'rentalpost'):
        specific_post = post.rentalpost

    #รายละเอียดโพสต์
    # post = (
    # Post.objects
    # .select_related('author')
    # .prefetch_related('media', 'skills', 'categories')
    # .filter(pk=post_id)
    # .first()
    # )
    
    #dic ที่จะส่งข้อมูลไปหน้า html
    context = {
        #ส่งรายโพสต์ hiring or rent
        'post': specific_post,
        #ส่งชุดรูปภาพทั้งหมด
        'media': post.media.all(), 
    }
    
    return render(request, 'pages/detail_post.html', context) 
