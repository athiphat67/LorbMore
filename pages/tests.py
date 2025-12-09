from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from posts.models import HiringPost, RentalPost, Media
from posts.views import _format_post_data
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from pages.forms import StudentRegisterForm
from django.contrib import messages
from .forms import ContactForm


class PagesViewTests(TestCase):
    # กำหนดข้อมูลโพสต์ขึ้นมาเอง
    def setUp(self):
        self.user = User.objects.create_user(username = 'minnie', password = 'minn9149')
    
        # สร้าง hiring post 5 โพสต์
        for i in range(5):
            post = HiringPost.objects.create(
                author = self.user,
                title = f"post {i}: รับจ้างถ่ายรูปปริญญา",
                budgetMin = 600,
                budgetMax = 1500,
            )
        # สร้างรูปมา 2 รูป ในแต่ละโพสต์
            for j in range(1, 3):
                Media.objects.create(
                    post=post,
                    image=SimpleUploadedFile(
                        name=f"hiring_{i}_{j}.jpg",
                        content=b"",
                        content_type="image/jpeg"
                    )
                )
                
        # สร้าง rental post 5 โพสต์
        for i in range(5):
            post = RentalPost.objects.create(
                author = self.user,
                title = f"post {i}: ให้เช่ายืมกล้องถ่ายรูป",
                pricePerDay = 100,
                deposit = 2,
            )
            # สร้างรูปมา 2 รูป ในแต่ละโพสต์
            for j in range(1, 3):
                Media.objects.create(
                    post=post,
                    image=SimpleUploadedFile(
                        name=f"rental_{i}_{j}.jpg",
                        content=b"cokkie",
                        content_type="image/jpeg"
                    )
                )
    
    
    def test_about_page_status(self):
        # สร้าง URL จากชื่อของ path name
        url = reverse("about")
        
        # จำลองการเปิดหน้าเว็บด้วย HTTP GET เช่นเดียวกับที่ browser ทำจริง
        response = self.client.get(url)
        
        # ตรวจสอบว่า status code ของ response เท่ากับ 200 หรือโหลดหน้าเว็บสำเร็จ
        self.assertEqual(response.status_code, 200)
        
        # ตรวจสอบ template ที่ใช้ถูกต้องหรือไม่
        self.assertTemplateUsed(response, "pages/about.html")

    
    def test_home_page_status_context_and_template(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # ตรวจสอบ template ที่ใช้ถูกต้องหรือไม่
        self.assertTemplateUsed(response, "pages/home.html")

        self.assertIn("hiring_items", response.context)
        self.assertIn("rental_items", response.context)

        # จำกัดมีโพสต์มากสุด 3 โพสต์
        self.assertLessEqual(len(response.context["hiring_items"]), 3)
        self.assertLessEqual(len(response.context["rental_items"]), 3)
    
    
    def test_home_page_latest_items_order(self):
        url = reverse("home")
        response = self.client.get(url)

        hiring_items = response.context["hiring_items"]
        rental_items = response.context["rental_items"]

        # ดึงค่า id ของแต่ละโพสต์มาเรียงเป็น list ใหม่
        hiring_ids = [item["id"] for item in hiring_items]
        rental_ids = [item["id"] for item in rental_items]
        
        # ตรวจสอบว่าลำดับในหน้าเว็บตรงกับ id โพสต์ มากไปน้อยหรือไม่
        self.assertEqual(hiring_ids, sorted(hiring_ids, reverse=True))
        self.assertEqual(rental_ids, sorted(rental_ids, reverse=True))
    
    
    # ทดสอบ prefetch media  
    def test_home_page_prefetch_media(self):
        url = reverse("home")
        response = self.client.get(url)

        hiring_items = response.context["hiring_items"]
        rental_items = response.context["rental_items"]

        # ตรวจว่ารูปแรกของแต่ละโพสต์ถูกเอาใช้งาน
        for item in hiring_items:
            
            # ดึงข้อมูลโพสต์ตัวจริงจากฐานข้อมูลที่มี id เดียวกับใน item
            post_obj = HiringPost.objects.get(id=item["id"])
            
            # ดึง URL ของรูปแรกของโพสต์ในฐานข้อมูล เพื่อใช้เป็นตัวทดสอบ
            expected_image = post_obj.media.first().image.url
            
            # ตรวจสอบว่า "image_url" ที่ view ส่งออกมาตรงกับ URL ของรูปจริงในฐานข้อมูล
            self.assertEqual(item["image_url"], expected_image)

        for item in rental_items:
            post_obj = RentalPost.objects.get(id=item["id"])
            expected_image = post_obj.media.first().image.url
            self.assertEqual(item["image_url"], expected_image)
            
        # ตรวจว่า index 0 = โพสต์ล่าสุด
        hiring_ids = [item["id"] for item in hiring_items]
        rental_ids = [item["id"] for item in rental_items]
        
        #ตรวจสอบว่า hiring_items ถูกเรียงจากโพสต์ใหม่ไปโพสต์เก่าสุด 
        self.assertEqual(hiring_ids, sorted(hiring_ids, reverse=True))
        self.assertEqual(rental_ids, sorted(rental_ids, reverse=True))
    
    
    # ทดสอบ format ว่าตรงกับโพสต์ 
    # เอา hiring post โพสต์ 1 เป็นทดสอบ
    def test_format_post_data_function(self):
        post = HiringPost.objects.first()
        post.images = list(post.media.all())  # จำลอง prefetch
        formatted = _format_post_data(post)

        self.assertEqual(formatted["id"], post.id)
        self.assertIn("title", formatted)
        self.assertIn("image_url", formatted)  # ต้องมี
        self.assertIn("reviews", formatted)
        self.assertIn("rating", formatted)
        self.assertIn("price_detail", formatted)
        
        #นับจำนวนรูปด้วย ว่ามีครบตามที่ระบุจำนวนรูปไปมั้ย
        #self.assertEqual(len(formatted["images"]), 2)
        
class StudentRegisterFormTest(TestCase):
    def setUp(self): 
        # กำหนดข้อมูล user 
        self.user = User.objects.create_user(
            username='john0',
            email='john.doe@dome.tu.ac.th',
            password='Password123!'
        )
        
    # email ตรงตาม form ที่กำหนดและสามารถใช้งานได้    
    def test_email_valid(self):
        form_data = {
            'username': 'john1', 
            'email': 'john.do@dome.tu.ac.th', 
            'password1': 'Password123!', 
            'password2': 'Password123!'
        }
        form = StudentRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'john.do@dome.tu.ac.th')
    
    # email ไม่ตรงตาม form ที่กำหนด => ไม่มีจุด
    def test_email_no_dot(self):
        form_data = {
            'username': 'john2',
            'email': 'john@dome.tu.ac.th',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = StudentRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("กรุณากรอก email ให้ถูกต้อง", form.errors['email'][0])
    
    # email ไม่ตรงตาม form ที่กำหนด => ยาวเกินกำหนด
    def test_email_surname_too_long(self):
        form_data = {
            'username': 'john3',
            'email': 'john.surname@dome.tu.ac.th',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = StudentRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("กรุณากรอก email ให้ถูกต้อง", form.errors['email'][0])
        
    # email ซ้ำกันกับที่เรากำหนดใน setUp
    def test_email_duplicate(self):
        form_data = {
            'username': 'john0',
            'email': 'john.doe@dome.tu.ac.th',
            'password1': 'Password',
            'password2': 'Password',
        }
        form = StudentRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("อีเมลนี้ถูกใช้งานไปแล้ว", form.errors['email'][0])
        
    # ไม่ใช่ email ของนักศึกษามธ.
    def test_email_not_dome_domain(self):
        form_data = {
            'username': 'user4',
            'email': 'someone@gmail.com',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }
        form = StudentRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
class RegisterViewTest(TestCase):
    def setUp(self):
        self.url = reverse('register')  # ชื่อ url ของ register_view
        self.user_data = {
            'username': 'john',
            'email': 'john.doe@dome.tu.ac.th',
            'password1': 'Password123!',
            'password2': 'Password123!',
        }

    # ทดสอบเปิดหน้า register
    def test_register_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
        
        # ตรวจสอบ context ของ template มี key 'form' และ object ส่งไป StudentRegisterForm
        self.assertIsInstance(response.context['form'], StudentRegisterForm)

    # จำลองการ submit 
    def test_register_post_valid(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertRedirects(response, reverse('home'))
        # ตรวจสอบว่าผ user ถูกสร้าง
        user_exists = User.objects.filter(username='john').exists()
        self.assertTrue(user_exists)

    # จำลองการในตอนสร้างข้อมูลไม่ถูกต้อง
    def test_register_post_invalid(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'johndoe@dome.tu.ac.th'  # ไม่มีจุด → invalid
        response = self.client.post(self.url, invalid_data)

        # status code ต้องเป็น 200 เพราะไม่ได้ redirect
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบว่า template ใช้ form ถูกต้อง
        self.assertTemplateUsed(response, 'registration/register.html')

        # ดึง form จาก context
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn("กรุณากรอก email ให้ถูกต้อง", form.errors['email'])
        
# ทดสอบ contact page view
class ContactViewTests(TestCase):
    def test_get_contact_view(self):
        # แปลงชื่อ URL path 'contact' เป็น URL จริง
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/contact.html')
        self.assertIn('form', response.context)

    def test_post_valid_form(self):
        form_data = {
            'name': 'John Doe',
            'email': 'john.doe@dome.tu.ac.th',
            'subject': 'Test Subject',
            'message': 'Hello, this is a test message.'
        }
        
        # ตรวจสอบว่า response เป็น redirect (status code 302) เพราะ form valid → view redirect หลังบันทึก
        response = self.client.post(reverse('contact'), data=form_data)
        
        # เช็คว่า redirect กลับหน้า contact
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('contact'))

        # เช็คว่ามี message success ถูกส่ง
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Message sent successfully' in str(m) for m in messages))

    def test_post_invalid_form(self):
        # ส่ง email ว่าง จะทำให้ form invalid
        form_data = {
            'name': 'John Doe',
            'email': '',  # invalid
            'message': 'Hello'
        }
        response = self.client.post(reverse('contact'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/contact.html')
        # เช็คว่ามี form อยู่ใน context
        self.assertIn('form', response.context)

        # เช็คว่าฟิลด์ email มี error
        self.assertIn('email', response.context['form'].errors)

         