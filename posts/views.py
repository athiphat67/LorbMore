from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, HiringPost, RentalPost, Media, Review
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import HiringPostForm, RentalPostForm
from .decorators import student_required
from django.db.models import Q 
from itertools import chain

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
    formatted_items = [_format_post_data(post, request.user) for post in page_obj]

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
    formatted_items = [_format_post_data(post, request.user) for post in page_obj]

    context = {
        "rental_items": formatted_items,
        "page_obj": page_obj,  # ส่ง 'page_obj' ไปให้ Template
    }
    return render(request, "pages/rental.html", context)


# ฟังก์ชันช่วยในการแปลงข้อมูลจาก ORM object เป็น Dict
def _format_post_data(post, user=None):
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

    is_booked = False
    if user and user.is_authenticated:
        # เช็คว่า id ของ user นี้ อยู่ใน list bookings ของโพสต์นี้ไหม
        is_booked = post.bookings.filter(id=user.id).exists()

    # ส่งค่าในรูป Dic กลับไป
    return {
        "id": post.id,
        "image_url": first_image_url or "/static/img/default.png",
        # "images": images,
        "title": post.title,
        "count_reviews": post.count_reviews,
        "avg_rating": post.avg_rating,
        "price_detail": price_detail,
        "is_booked": is_booked,
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

    is_booked = False
    if request.user.is_authenticated:
        is_booked = post.bookings.filter(id=request.user.id).exists()

    context = {
        "post": specific_post,
        "media": post.media.all(),
        "skills": skills_list,
        "categories": post.categories.all(),
        "is_hiring": is_hiring,
        "is_booked": is_booked,
    }

    return render(request, "pages/detail_post.html", context)


def createpost(request):
    return render(request, "pages/createposts.html")


@student_required
def create_hiring_view(request):
    if request.method == "POST":
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

            files = request.FILES.getlist("images")
            for f in files:
                # สร้าง Media object ที่เชื่อมโยงกับ new_post
                Media.objects.create(post=new_post, image=f)

            # ส่งผู้ใช้ไปยังหน้า detail ของโพสต์ที่เพิ่งสร้าง
            return redirect("posts:detail_post", post_id=new_post.id)
    else:
        form = HiringPostForm()

    context = {"form": form, "form_title": "Create hiring post"}
    return render(request, "pages/create_hiring.html", context)


@student_required
def create_rental_view(request):
    if request.method == "POST":
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

            files = request.FILES.getlist("images")
            for f in files:
                # สร้าง Media object ที่เชื่อมโยงกับ new_post
                Media.objects.create(post=new_post, image=f)

            # ส่งผู้ใช้ไปยังหน้า detail ของโพสต์ที่เพิ่งสร้าง
            return redirect("posts:detail_post", post_id=new_post.id)
    else:
        form = RentalPostForm()

    context = {"form": form, "form_title": "Create rental post"}
    return render(request, "pages/create_rental.html", context)


@login_required
def my_post_view(request):
    user = request.user

    # ดึงข้อมูล Media มารอไว้ (เพื่อแสดงรูปภาพปก)
    posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

    # ดึง Post ของ User นั้นๆ ทั้ง Hiring และ Rental
    my_hiring = HiringPost.objects.filter(author=user).prefetch_related(
        posts_with_media
    )
    my_rental = RentalPost.objects.filter(author=user).prefetch_related(
        posts_with_media
    )

    # รวมลิสต์และเรียงลำดับจาก "เก่า -> ใหม่" (ตาม id น้อยไปมาก)
    all_my_posts = sorted(list(my_hiring) + list(my_rental), key=lambda x: x.id)

    # แปลงข้อมูลให้อยู่ในรูปแบบ Dict
    formatted_items = [_format_post_data(post) for post in all_my_posts]

    can_create = user.is_superuser or user.email.endswith("@dome.tu.ac.th")

    context = {
        "mypost_items": formatted_items,
        "can_create": can_create,
    }
    return render(request, "pages/mypost.html", context)


@login_required
def delete_post_view(request, post_id):
    # ดึง Post หลัก
    post = get_object_or_404(Post, pk=post_id)

    # ตรวจสอบว่าเป็นเจ้าของโพสต์หรือไม่
    if post.author != request.user:
        return redirect("posts:detail_post", post_id=post.id)

    # ลบโพสต์
    post.delete()
    return redirect("posts:mypost")


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # ตรวจสอบว่าเป็นเจ้าของโพสต์
    if post.author != request.user:
        return redirect("posts:detail_post", post_id=post.id)

    # เช็คประเภทโพสต์เพื่อเลือก Form ที่ถูกต้อง
    instance = None
    form_class = None
    template_name = ""

    if hasattr(post, "hiringpost"):
        instance = post.hiringpost
        form_class = HiringPostForm
        template_name = "pages/create_hiring.html"  # ใช้หน้าเดียวกับ create แต่มีข้อมูลเดิม
        title_context = "Edit your hiring post"
    elif hasattr(post, "rentalpost"):
        instance = post.rentalpost
        form_class = RentalPostForm
        template_name = "pages/create_rental.html"
        title_context = "Edit your rental post"
    else:
        return redirect("posts:mypost")

    if request.method == "POST":
        # ส่ง instance เข้าไปเพื่อเป็นการ Update
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            updated_post = form.save()

            files = request.FILES.getlist("images")
            for f in files:
                Media.objects.create(post=updated_post, image=f)

            return redirect("posts:detail_post", post_id=updated_post.id)
    else:
        # แสดงฟอร์มพร้อมข้อมูลเดิม
        form = form_class(instance=instance)

    context = {
        "form": form,
        "form_title": title_context,
        "is_edit": True,  # ตัวแปรบอก Template ว่ากำลัง Edit อยู่ (เผื่อใช้ปรับคำในปุ่ม)
    }
    return render(request, template_name, context)


@login_required
def add_review_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # ป้องกันไม่ให้เจ้าของโพสต์รีวิวตัวเอง (Optional)
    if post.author == request.user:
        # อาจจะ redirect กลับพร้อมแจ้งเตือนว่ารีวิวไม่ได้
        return redirect("posts:detail_post", post_id=post.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        
        # ใช้คำสั่ง update_or_create
        # ความหมาย: ถ้ามี (post+author) นี้อยู่แล้ว ให้ 'อัปเดต' rating/comment
        # ถ้ายังไม่มี ให้ 'สร้างใหม่'
        Review.objects.update_or_create(
            post=post,
            author=request.user,
            defaults={"rating": rating, "comment": comment},
        )
            
    # ถ้าไม่ใช่ POST ให้ redirect กลับไปหน้า post detail เลย
    return redirect("posts:detail_post", post_id=post.id)


@login_required
def toggle_booking_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # เช็คว่า user จองไปหรือยัง
    if post.bookings.filter(id=request.user.id).exists():
        post.bookings.remove(request.user)  # ถ้ามีแล้ว ให้ลบออก (Un-book)
    else:
        post.bookings.add(request.user)  # ถ้ายังไม่มี ให้เพิ่ม (Book)

    # Redirect กลับไปหน้าเดิมที่ user กดมา
    return redirect(request.META.get("HTTP_REFERER", "posts:hiring"))


@login_required
def my_booking_view(request):
    user = request.user

    # ดึง Media มารอไว้
    posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

    # ดึงโพสต์ที่ user นี้อยู่ใน field bookings
    # ต้อง select_related hiringpost/rentalpost เพื่อให้แยกประเภทได้ตอน format
    booked_posts = (
        Post.objects.filter(bookings=user)
        .select_related("hiringpost", "rentalpost")
        .prefetch_related(posts_with_media)
        .order_by("-id")
    )

    # แปลงข้อมูล (ดึง instance ลูก hiring/rental ออกมาส่งให้ format)
    formatted_items = []
    for post in booked_posts:
        # ต้องแปลงเป็น HiringPost หรือ RentalPost object ก่อนส่งเข้า format
        actual_post = post
        if hasattr(post, "hiringpost"):
            actual_post = post.hiringpost
        elif hasattr(post, "rentalpost"):
            actual_post = post.rentalpost
        if hasattr(post, "images"):
            actual_post.images = post.images

        formatted_items.append(_format_post_data(actual_post, user))

    context = {
        "booking_items": formatted_items,
    }
    return render(request, "pages/mybooking.html", context)

def search_view(request):
    query = request.GET.get('q') 
    formatted_items = []

    if query:
        posts_with_media = Prefetch("media", queryset=Media.objects.all(), to_attr="images")

        # 1. ค้นหาใน HiringPost (ค้นหาจาก Title หรือ Description)
        hiring_results = HiringPost.objects.select_related('author').prefetch_related(posts_with_media).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(skills__name__icontains=query) # (Option) ค้นหาจาก Skill ด้วยก็ได้
        ).distinct()

        # 2. ค้นหาใน RentalPost
        rental_results = RentalPost.objects.select_related('author').prefetch_related(posts_with_media).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(categories__name__icontains=query) # (Option) ค้นหาจาก Category ด้วยก็ได้
        ).distinct()

        # 3. รวมผลลัพธ์เข้าด้วยกัน (ใช้ chain เพื่อรวม QuerySet 2 ตัว)
        # หรือจะแปลงเป็น list แล้วบวกกันก็ได้: all_results = list(hiring_results) + list(rental_results)
        all_results = sorted(
            list(hiring_results) + list(rental_results), 
            key=lambda x: x.id, 
            reverse=True # เรียงจากใหม่ไปเก่า
        )

        # 4. ใช้ฟังก์ชันเดิมจัดรูปแบบข้อมูล
        formatted_items = [_format_post_data(post, request.user) for post in all_results]

    context = {
        "query": query,
        "search_items": formatted_items,
        "result_count": len(formatted_items)
    }
    return render(request, "pages/search.html", context)