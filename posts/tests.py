from django.test import TestCase, Cient
from django.urls import reverse
from django.contrib.auth.models import User
from .models import RentalPost, HiringPost, Media, Skill, Category
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
class PostIntegrationTestCase(TestCase):
    def setUp(self):
        # สร้างผู้ใช้งาน
        user = User.object.create_user(username = 'minnie', password = 'minn9149')
        client = Client()
        
        # สร้าง Skill & Category
        skills = Skill.object.create(name = 'Photoshop')
        categories = Category.object.create(name = 'Photo', kind = 'hiring')
        
        #สร้าง hiring post ที่มีอย่างน้อย 8 โพสต์
        hiring_post = []
        for i in range(8):
            post = HiringPost.objects.create(
                author = user,
                title = f"post {i}: รับจ้างถ่ายรูปปริญญา",
                budgetMin = 600,
                budgetMax = 1500,
            )
            
        post.skills.add(self.skill)
        post.categories.add(self.catrgory)
        
        Media.objects.create(
            post = post,
            image=SimpleUploadedFile(name=f'test{i}.jpg', content=b'', content_type='image/jpeg'),
        )
        self.hiring_post.append(post)
        
        #สร้าง rental post ที่มีอย่างน้อย 8 โพสต์
        rental_post = []
        for i in range(8):
            post = RentalPost.objects.create(
                author = user,
                title = f"post {i}: ให้เช่ายืมกล้องถ่ายรูป",
                pricePerDay = 100,
                deposit = 2,
            )
        post.categories.add(self.category)
        self.rental_post.append(post)
        
    def test_hiring_page_status_and_paginator(self):
        # หน้า hiring page จะต้องมี post มากสุดหกอัน
        url = reverse('posts:hiring')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hiring_items', response.context)
    
        # หน้าหนึ่ง ต้องมี 6 โพสต์
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

        # หน้าหนึ่ง ต้องมี 2 โพสต์ (8-6=2)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)
    
    def test_hiring_items_format(self):
        url = reverse('posts:hiring')
        response = self.client.get(url)
        formatted_item = response.context['hiring_items'][0]
    
        # ตรวจสอบว่า expected_keys ที่เรากำหนดตรงกับ formatted_item เปล่า
        expected_keys = ['id', 'image_url', 'title', 'reviews', 'rating', 'price_detail']
        for key in expected_keys:
            self.assertIn(key, formatted_item)
        
        # ตรวจสอบว่า price_detail มี "/วัน" สำหรับ RentalPost
        self.assertIn('เริ่มต้น', formatted_item['price_detail'])    
    
    def test_rental_page_status_and_paginator(self):
        # หน้า rental page จะต้องมี post มากสุดหกอัน
        url = reverse('posts:rental')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rental_items', response.context)
    
        # หน้าหนึ่ง ต้องมี 6 โพสต์
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

        # หน้าหนึ่ง ต้องมี 2 โพสต์ (8-6=2)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)
    
    def test_rental_items_format(self):
        url = reverse('posts:rental')
        response = self.client.get(url)
        formatted_item = response.context['rental_items'][0]
    
        # ตรวจสอบว่า expected_keys ที่เรากำหนดตรงกับ formatted_item เปล่า
        expected_keys = ['id', 'image_url', 'title', 'reviews', 'rating', 'price_detail']
        for key in expected_keys:
            self.assertIn(key, formatted_item)
        
        # ตรวจสอบว่า price_detail มี "/วัน" สำหรับ RentalPost
        self.assertIn('/วัน', formatted_item['price_detail'])
    
    def test_detail_post_hiring(self):
        post = self.hiring_posts[0]
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
        # ตรวจสอบ is_hiring
        self.assertTrue(response.context['is_hiring'])
    
        # ตรวจสอบ media
        media = list(response.context['media'])
        self.assertEqual(len(media), 1)
    
        # ตรวจสอบ skills
        skills = list(response.context['skills'])
        self.assertIn(self.skill, skills)

        # ตรวจสอบ categories
        categories = list(response.context['categories'])
        self.assertIn(self.category, categories)
    
    def test_detail_post_rental(self):
        post = self.hiring_posts[0]
        url = reverse('posts:detail_post', args=[post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบ is_hiring
        self.assertFalse(response.context['is_hiring'])

        # Rental post ไม่มี skills
        self.assertIsNone(response.context['skills'])

        # ตรวจสอบ media (ยังไม่มี media) -> ควรเป็น empty queryset
        media = list(response.context['media'])
        self.assertEqual(media, [])

        # ตรวจสอบ categories
        categories = list(response.context['categories'])
        self.assertIn(self.category, categories)
        