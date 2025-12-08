from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, HiringPost, RentalPost, Media
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import HiringPostForm, RentalPostForm
from .decorators import student_required 

# Create your views here.
def hiring_page_view(request):
    posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

    # ดึง "QuerySet" ทั้งหมดมา
    all_hiring_posts = HiringPost.objects.prefetch_related(posts_with_media).order_by(
        "-id"
    )

    # สร้าง Paginator (ตั้งค่า 6 โพสต์ต่อหน้า)
    paginator = Paginator(all_hiring_posts, 6)

    # ดึงเลขหน้าจาก URL
    page_number = request.GET.get("page")

    # ดึงข้อมูล "หน้า" ที่ถูกต้องมา
    page_obj = paginator.get_page(page_number)
    formatted_items = [_format_post_data(post) for post in page_obj]

    context = {
        "hiring_items": formatted_items,
        "page_obj": page_obj,  # ส่ง 'page_obj' ไปให้ Template
    }
    return render(request, "pages/hiring.html", context)


def rental_page_view(request):
    posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

    # ดึง "QuerySet" ทั้งหมดมา
    all_rental_posts = RentalPost.objects.prefetch_related(posts_with_media).order_by(
        "-id"
    )

    # สร้าง Paginator (6 โพสต์ต่อหน้า)
    paginator = Paginator(all_rental_posts, 6)

    # ดึงเลขหน้าจาก URL
    page_number = request.GET.get("page")

    # ดึงข้อมูล "หน้า" ที่ถูกต้องมา
    page_obj = paginator.get_page(page_number)
    formatted_items = [_format_post_data(post) for post in page_obj]

    context = {
        "rental_items": formatted_items,
        "page_obj": page_obj,  # ส่ง 'page_obj' ไปให้ Template
    }
    return render(request, "pages/rental.html", context)


# ฟังก์ชันช่วยในการแปลงข้อมูลจาก ORM object เป็น Dict
def _format_post_data(post):
    """
    ฟังก์ชันช่วยแปลงข้อมูลจาก ORM Object -> Dict
    เพื่อส่งต่อไปยัง Template (HTML)
    """

    # ดึงรูปภาพแรกของโพสต์ (ถ้ามี) ตอนนี้พวกเรายังไม่มีลิ้งค์ใส่รูปภาพ
    first_image_url = None
    if hasattr(post, "images") and post.images:
        first_media = post.images[0]
        if first_media.image:
            first_image_url = first_media.image.url

    # กำหนดชื่อและราคาตามประเภทโพสต์
    price_detail = ""
    if isinstance(post, HiringPost):
        price_detail = f"เริ่มต้น {post.budgetMin:,}฿"
    elif isinstance(post, RentalPost):
        price_detail = f"เริ่มต้น {post.pricePerDay:,}฿/วัน"

    # ส่งค่าในรูป Dic กลับไป
    return {
        "id": post.id,
        "image_url": first_image_url or "/static/img/default.png",
        # "images": images,
        "title": post.title,
        # ตอนนี้มันยังไม่มีระบบให้คะแนน เลยสมมติค่านี้ไปก่อนนะ
        "reviews": 27 if isinstance(post, HiringPost) else 13,
        "rating": 4.8 if isinstance(post, HiringPost) else 4.5,
        "price_detail": price_detail,
    }


def detail_post_view(request, post_id):

    post = get_object_or_404(
        Post.objects.select_related(
            "author", "hiringpost", "rentalpost"
        ).prefetch_related(  
            "media",  # ดึงจาก Post
            "categories",  # ดึงจาก Post
            "hiringpost__skills",  # ดึง skills ที่อยู่ *ข้างใน* hiringpost (M2M)
        ),
        pk=post_id,
    )

    specific_post = post
    skills_list = None
    is_hiring = False

    if hasattr(post, "hiringpost"):
        specific_post = post.hiringpost
        skills_list = post.hiringpost.skills.all()
        is_hiring = True

    elif hasattr(post, "rentalpost"):
        specific_post = post.rentalpost

    context = {
        "post": specific_post,  
        "media": post.media.all(), 
        "skills": skills_list,  
        "categories": post.categories.all(), 
        "is_hiring" : is_hiring, 
    }

    return render(request, "pages/detail_post.html", context)


def createpost(request):
    return render(request, "pages/createposts.html")

@student_required
def create_hiring_view(request):
    if request.method == 'POST':
        form = HiringPostForm(request.POST, request.FILES) 
        if form.is_valid():
            # บันทึกฟอร์มหลัก แต่ยังไม่ commit ลง DB
            new_post = form.save(commit=False)
            
            # กำหนด 'author' ให้เป็น user ที่ login อยู่
            new_post.author = request.user 
            
            # บันทึก post หลักลง DB (ตอนนี้ post จะมี id แล้ว)
            new_post.save()
            
            # บันทึก M2M (categories, skills)
            form.save_m2m() 
            
            files = request.FILES.getlist('images')
            for f in files:
                # สร้าง Media object ที่เชื่อมโยงกับ new_post
                Media.objects.create(post=new_post, image=f)
            
            # ส่งผู้ใช้ไปยังหน้า detail ของโพสต์ที่เพิ่งสร้าง
            return redirect('posts:detail_post', post_id=new_post.id) 
    else:
        form = HiringPostForm()

    context = {
        'form': form,
        'form_title': 'Create your hiring post'
    }
    return render(request, 'pages/create_hiring.html', context)

@student_required
def create_rental_view(request):
    if request.method == 'POST':
        form = RentalPostForm(request.POST, request.FILES) 
        if form.is_valid():
            # บันทึกฟอร์มหลัก แต่ยังไม่ commit ลง DB
            new_post = form.save(commit=False)
            
            # กำหนด 'author' ให้เป็น user ที่ login อยู่
            new_post.author = request.user 
            
            # บันทึก post หลักลง DB (ตอนนี้ post จะมี id แล้ว)
            new_post.save()
            
            # บันทึก M2M (categories, skills)
            form.save_m2m() 
            
            files = request.FILES.getlist('images')
            for f in files:
                # สร้าง Media object ที่เชื่อมโยงกับ new_post
                Media.objects.create(post=new_post, image=f)
            
            # ส่งผู้ใช้ไปยังหน้า detail ของโพสต์ที่เพิ่งสร้าง
            return redirect('posts:detail_post', post_id=new_post.id) 
    else:
        form = RentalPostForm()

    context = {
        'form': form,
        'form_title': 'Create your rental post'
    }
    return render(request, 'pages/create_rental.html', context)

@login_required
def my_post_view(request):
    user = request.user
    
    # ดึงข้อมูล Media มารอไว้ (เพื่อแสดงรูปภาพปก)
    posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

    # ดึง Post ของ User นั้นๆ ทั้ง Hiring และ Rental
    my_hiring = HiringPost.objects.filter(author=user).prefetch_related(posts_with_media)
    my_rental = RentalPost.objects.filter(author=user).prefetch_related(posts_with_media)

    # รวมลิสต์และเรียงลำดับจาก "เก่า -> ใหม่" (ตาม id น้อยไปมาก)
    all_my_posts = sorted(
        list(my_hiring) + list(my_rental),
        key=lambda x: x.id 
    )

    # แปลงข้อมูลให้อยู่ในรูปแบบ Dict
    formatted_items = [_format_post_data(post) for post in all_my_posts]

    context = {
        "mypost_items": formatted_items,
    }
    return render(request, "pages/mypost.html", context)

@login_required
def delete_post_view(request, post_id):
    # ดึง Post หลัก
    post = get_object_or_404(Post, pk=post_id)

    # ตรวจสอบว่าเป็นเจ้าของโพสต์หรือไม่
    if post.author != request.user:
        return redirect('posts:detail_post', post_id=post.id)

    # ลบโพสต์
    post.delete()
    return redirect('posts:mypost')

@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # ตรวจสอบว่าเป็นเจ้าของโพสต์
    if post.author != request.user:
        return redirect('posts:detail_post', post_id=post.id)

    # เช็คประเภทโพสต์เพื่อเลือก Form ที่ถูกต้อง
    instance = None
    form_class = None
    template_name = ""
    
    if hasattr(post, 'hiringpost'):
        instance = post.hiringpost
        form_class = HiringPostForm
        template_name = 'pages/create_hiring.html' # ใช้หน้าเดียวกับ create แต่มีข้อมูลเดิม
        title_context = "Edit your hiring post"
    elif hasattr(post, 'rentalpost'):
        instance = post.rentalpost
        form_class = RentalPostForm
        template_name = 'pages/create_rental.html'
        title_context = "Edit your rental post"
    else:
        return redirect('posts:mypost')

    if request.method == 'POST':
        # ส่ง instance เข้าไปเพื่อเป็นการ Update
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            updated_post = form.save()
            form.save_m2m() # บันทึก Skills/Categories

            # เพิ่มรูปภาพใหม่ (ถ้ามีการอัปโหลดเพิ่ม)
            files = request.FILES.getlist('images')
            for f in files:
                Media.objects.create(post=updated_post, image=f)

            return redirect('posts:detail_post', post_id=updated_post.id)
    else:
        # แสดงฟอร์มพร้อมข้อมูลเดิม
        form = form_class(instance=instance)

    context = {
        'form': form,
        'form_title': title_context,
        'is_edit': True # ตัวแปรบอก Template ว่ากำลัง Edit อยู่ (เผื่อใช้ปรับคำในปุ่ม)
    }
    return render(request, template_name, context)
