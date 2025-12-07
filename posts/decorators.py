from django.contrib.auth.decorators import user_passes_test

def is_student_or_admin(user):
    # ยอมรับถ้า: 
    # 1. เป็น Admin (is_superuser) หรือ Staff
    # 2. อีเมลลงท้ายด้วย @dome.tu.ac.th
    return user.is_authenticated and (
        user.is_superuser or 
        user.email.endswith('@dome.tu.ac.th')
    )

# สร้าง Decorator เอาไว้แปะบน View
student_required = user_passes_test(
    is_student_or_admin, 
    login_url='login', 
    redirect_field_name=None
)