from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm
from django.db.models import Avg
from posts.models import Review

def profile_detail_view(request, username): 
    
    profile_user = get_object_or_404(User, username=username)
    user_reviews = Review.objects.filter(post__author=profile_user).order_by('-created_at')
    avg_rating = user_reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating is None:
        avg_rating = 0
    else:
        avg_rating = round(avg_rating, 1) # ทศนิยม 1 ตำแหน่ง

    context = {
        'profile_user': profile_user,
        'user_reviews': user_reviews, # ส่งลิสต์รีวิวไป
        'avg_rating': avg_rating,     # ส่งคะแนนเฉลี่ยไป
        'review_count': user_reviews.count() # จำนวนรีวิว
    }
    return render(request, 'users/profile_detail.html', context)


# ฟังก์ชันสำหรับ "แก้ไขโปรไฟล์" (ต้อง Login เท่านั้น)
@login_required
def profile_edit_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile_detail", username=request.user.username)
        else:
            # เพิ่มบรรทัดนี้เพื่อเช็ค Error ใน Terminal
            print("User Form Errors:", u_form.errors)
            print("Profile Form Errors:", p_form.errors)

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile_edit.html", context)
