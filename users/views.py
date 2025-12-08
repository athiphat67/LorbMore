from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm

# ฟังก์ชันสำหรับ "ดูโปรไฟล์" (ใครเข้าก็ได้ หรือจะบังคับ login ก็ได้)
def profile_detail_view(request, username):
    # ค้นหา User จาก username ที่ส่งมาใน URL
    profile_user = get_object_or_404(User, username=username)
    
    context = {
        'profile_user': profile_user,
    }
    return render(request, 'users/profile_detail.html', context)

# ฟังก์ชันสำหรับ "แก้ไขโปรไฟล์" (ต้อง Login เท่านั้น)
@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile_detail', username=request.user.username) 

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile_edit.html', context)