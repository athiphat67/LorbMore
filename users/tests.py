from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from users.forms import UserUpdateForm, ProfileUpdateForm


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
        self.user = User.objects.create_user(username='testuser', password='123456')
        self.client = Client()
        self.client.login(username='testuser', password='123456')
        self.url = reverse('profile')  # url ของ profile_view

    def test_profile_get(self):
        """GET request จะ render หน้า profile พร้อม form"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
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
        self.assertRedirects(response, self.url)

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
        self.assertTemplateUsed(response, 'users/profile.html')

        # ตรวจสอบว่ามี error ใน form
        self.assertTrue(response.context['u_form'].errors)
        self.assertIsInstance(response.context['p_form'], ProfileUpdateForm)

        # ข้อมูลใน database ไม่ถูกแก้ไข
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, '')
        