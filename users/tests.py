from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from posts.models import Post, Review 
from users.forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.admin.sites import AdminSite
from users.admin import ProfileAdmin
from django.core.files.uploadedfile import SimpleUploadedFile


# Create your tests here.
class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='minnie', password='123456')

    def test_profile_str(self):
        profile, created = Profile.objects.get_or_create(user=self.user, defaults={'displayName': 'Minnie'})
        self.assertEqual(str(profile), self.user.username)
        self.assertEqual(str(profile), "minnie")
        
class ProfileViewTests(TestCase):
    def setUp(self):
        # สร้าง user และ profile อัตโนมัติ (สมมติ Profile มี OneToOne กับ User)
        self.user = User.objects.create_user(username='john', password='123456')
        self.client = Client()
        self.client.login(username='john', password='123456')
        self.url = reverse('profile_edit')  

    def test_profile_get(self):
        """GET request จะ render หน้า profile พร้อม form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')
        self.assertIsInstance(response.context['u_form'], UserUpdateForm)
        self.assertIsInstance(response.context['p_form'], ProfileUpdateForm)

    def test_profile_post_valid(self):
        """POST request valid จะบันทึกข้อมูลและ redirect"""
        data = {
        # UserUpdateForm fields
        'username': 'john',
        'email': 'john.do@dome.tu.ac.th',
        'first_name': 'John',
        'last_name': 'Do',

        # ProfileUpdateForm fields
        'displayName': 'Johnny',
        'studentId': '12345678',
        'bioSkills': 'New bio for profile',
        'phoneNum': '0123456789',
        'socialMedia': '@johnny'
        }

        response = self.client.post(self.url, data)
        # ต้อง redirect ไป profile_detail ของ user ใหม่
        self.assertRedirects(
            response,
            reverse('profile_detail', kwargs={'username': 'john'})
        )

        # ตรวจสอบว่า user และ profile ถูกอัปเดต
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'john')
        self.assertEqual(self.user.email, 'john.do@dome.tu.ac.th')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Do')
        self.assertEqual(self.user.profile.displayName, 'Johnny')
        self.assertEqual(self.user.profile.studentId, '12345678')
        self.assertEqual(self.user.profile.bioSkills, 'New bio for profile')
        self.assertEqual(self.user.profile.phoneNum, '0123456789')
        self.assertEqual(self.user.profile.socialMedia, '@johnny')
        

    def test_profile_post_invalid(self):
        """POST request invalid จะไม่ redirect, render หน้าเดิมพร้อม error"""
        data = {
            'username': '',  # invalid, username ต้องไม่ว่าง
            'bio': 'Some bio'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')

        # ตรวจสอบว่ามี error ใน form
        self.assertTrue(response.context['u_form'].errors)
        self.assertIsInstance(response.context['p_form'], ProfileUpdateForm)

        # ข้อมูลใน database ไม่ถูกแก้ไข
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, '')
        
class ProfileAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)

        self.user = User.objects.create_user(username="test", password="123456")

    def test_show_image_with_file(self):
        # สร้างข้อมูลจำลอง
        image = SimpleUploadedFile(
            name="test.jpg",
            content=b"dummy image",
            content_type="image/jpeg"
        )

        profile = self.user.profile
        profile.profile_image = image
        profile.save()

        html = self.admin.show_image(profile)

        self.assertIn("<img", html)
        self.assertIn("profile_images", html)
        # self.assertIn("max-height: 100px", html)

    def test_show_image_without_file(self):
        profile = self.user.profile
        profile.profile_image = None
        profile.save()

        html = self.admin.show_image(profile)
        self.assertEqual(html, "-")

class ProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="john", password="12345")
        self.profile = self.user.profile
        self.profile.displayName = "John Doe"
        self.profile.save()

    def test_str_method(self):
        # __str__ ต้องคืนค่าเป็น username
        self.assertEqual(str(self.profile), "john")

    def test_get_average_rating_no_posts(self):
        # ถ้ายังไม่มีโพสต์เลย → return 0
        self.assertEqual(self.profile.get_average_rating(), 0)

    def test_get_average_rating_posts_no_reviews(self):
        # มีโพสต์แต่ไม่มีรีวิว → return 0
        Post.objects.create(author=self.user, title="Test Post")
        self.assertEqual(self.profile.get_average_rating(), 0)

    def test_get_average_rating_multiple_posts(self):
        # สร้างผู้ใช้ reviewer แยกต่างหาก
        reviewer1 = User.objects.create_user(username="alice", password="123")
        reviewer2 = User.objects.create_user(username="bob", password="123")
        
        # กรณีมีหลายโพสต์ (สร้าง โพสต์ 2 อัน ของเจ้าของโพสต์)
        post1 = Post.objects.create(author=self.user, title="Post 1")
        post2 = Post.objects.create(author=self.user, title="Post 2")

        Review.objects.create(post=post1, author=reviewer1, rating=4)
        Review.objects.create(post=post2, author=reviewer2, rating=5)
        
        # ตรวจสอบ view
        url = reverse('profile_detail', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        avg_view = response.context['avg_rating']
        self.assertIsInstance(avg_view, float)
        self.assertEqual(avg_view, 4.5)  # ตรวจสอบค่า avg ถูกต้องและปัดทศนิยม 1 ตำแหน่ง

        # ตรวจสอบ model method
        avg_model = self.profile.get_average_rating()
        self.assertIsInstance(avg_model, float)
        self.assertEqual(avg_model, 4.5)