from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, RentalPost, HiringPost, Media, Skill, Category
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
class PostIntegrationTestCase(TestCase):
    def setUp(self):
        self.skills = Skill.objects.create(name = 'Photoshop')
        
        # สร้างผู้ใช้งาน
        self.user = User.objects.create_user(username = 'minnie', password = 'minn9149')
        
        # สร้าง Skill & Category
        self.categories = Category.objects.create(name = 'Photo', kind = 'hiring')
        
        # สร้าง list ที่ใช้เก็บโพสต์แต่ละหมวด
        self.hiring_posts = []
        self.rental_posts = []
        
        # สร้างโพสต์ไว้ 8 โพสต์
        for i in range(8):
            post = HiringPost.objects.create(
                author = self.user,
                title = f"post {i}: รับจ้างถ่ายรูปปริญญา",
                budgetMin = 600,
                budgetMax = 1500,
            )
            
            # เพิ่ม skill ลงใน post
            post.skills.add(self.skills)
            post.categories.add(self.categories)
            
            # สร้างรูปภาพ 4 รูปภาพ
            for j in range(4):
                Media.objects.create(
                    post=post,
                    image=SimpleUploadedFile(
                        name=f"hiring_{i}_{j}.jpg",
                        content=b"cake",
                        content_type="image/jpeg"
                    )
                )
        
            # เพิ่ม post ลงใน list ของ hiring_post
            self.hiring_posts.append(post)
            
            # ถ้าหากไม่มีรูป จะทดสอบโดยการดึงรูปนี้ไป
            #media_without_image = Media.objects.create(post=post_for_test)
            #self.assertEqual(str(media_without_image), f"Media for Post ID: {post_for_test.id}")

        # สร้างโพสต์ไว้ 8 โพสต์
        for i in range(8):
            post = RentalPost.objects.create(
                author = self.user,
                title = f"post {i}: ให้เช่ายืมกล้องถ่ายรูป",
                pricePerDay = 100,
                deposit = 2,
            )
            
             # เพิ่ม skill ลงใน post
            post.categories.add(self.categories)
            
            for j in range(4):
                Media.objects.create(
                    post=post,
                    image=SimpleUploadedFile(
                        name=f"rental_{i}_{j}.jpg",
                        content=b"cookie",
                        content_type="image/jpeg"
                    )
                )
        
            # เพิ่ม post ลงใน list ของ rental_post
            self.rental_posts.append(post)
        
    def test_hiring_page_status_and_paginator(self):
        url = reverse('posts:hiring')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hiring_items', response.context)
    
        # หน้า hiring page จะต้องมี post มากสุด 6 โพสต์
        # หน้าแรห ต้องมี 6 โพสต์
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

        # หน้าสอง ต้องมี 2 โพสต์ (8-6=2)
        # response_page2 = self.client.get(url + '?page=2')
        # self.assertEqual(len(response.context['page_obj'].object_list), 2)
    
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
        url = reverse('posts:rental')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rental_items', response.context)
    
        # หน้า rental page จะต้องมี post มากสุด 6 โพสต์
        # หน้าแรห ต้องมี 6 โพสต์
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

        # หน้าสอง ต้องมี 2 โพสต์ (8-6=2)
        # response_page2 = self.client.get(url + '?page=2')
        # self.assertEqual(len(response.context['page_obj'].object_list), 2)
    
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
        url = reverse('posts:detail_post', args=[post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
        # ตรวจสอบ is_hiring
        self.assertTrue(response.context['is_hiring'])
    
        # ตรวจสอบ media
        media = list(response.context['media'])
        self.assertEqual(len(media), 4)
        
        # ตรวจสอบข้อมูล post
        post = response.context['post']
        self.assertEqual(post.id, self.hiring_posts[0].id)
        self.assertEqual(post.title, self.hiring_posts[0].title)
        self.assertEqual(post.budgetMin, self.hiring_posts[0].budgetMin)
        self.assertEqual(post.budgetMax, self.hiring_posts[0].budgetMax)
        
        #นับจำนวนรูปด้วย ว่ามีครบตามที่ระบุจำนวนรูปไปมั้ย 
        #self.assertEqual(len(formatted["images"]), 2)
        
    def test_detail_post_rental(self):
        post = self.rental_posts[0]
        url = reverse('posts:detail_post', args=[post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # ตรวจสอบ is_hiring
        self.assertFalse(response.context['is_hiring'])

        # Rental post ไม่มี skills
        self.assertIsNone(response.context['skills'])

        # ตรวจสอบ media (ยังไม่มี media) -> ควรเป็น empty queryset
        media = list(response.context['media'])
        self.assertEqual(len(media), 4)

        # ตรวจสอบ categories
        categories = list(response.context['categories'])
        self.assertIn(self.categories, categories)

        
        # ตรวจสอบว่าข้อมูล post ตรงกับที่สร้าง
        post = response.context['post']
        self.assertEqual(post.id, self.rental_posts[0].id)
        self.assertEqual(post.title, self.rental_posts[0].title)
        self.assertEqual(post.pricePerDay, self.rental_posts[0].pricePerDay)
        
        #นับจำนวนรูปด้วย ว่ามีครบตามที่ระบุจำนวนรูปไปมั้ย 
        #self.assertEqual(len(formatted["images"]), 2)
        
    # ถ้าไม่มีแล้วไม่ได้ 100  
    def test_model_str_methods(self):
        skill = Skill.objects.create(name="TestSkill")
        category = Category.objects.create(name="TestCat")
        rental = RentalPost.objects.create(author=self.user, title="Rent", pricePerDay=100)
        hiring = HiringPost.objects.create(author=self.user, title="Hire", budgetMin=100, budgetMax=200)
        media = Media.objects.create(post=rental)  # ไม่มี image
        post = Post.objects.create(author=self.user, title="Base Post")

        self.assertEqual(str(post), "Base Post")
        self.assertEqual(str(skill), "TestSkill")
        self.assertEqual(str(category), "TestCat")
        self.assertEqual(str(rental), "[Rental] Rent")
        self.assertEqual(str(hiring), "[Hiring] Hire")
        self.assertEqual(str(media), f"Media for Post ID: {rental.id}"),
    
    # ใส่รูปภาพ    
    def test_media_str_with_image(self):
        post = self.hiring_posts[0]
        # สร้าง Media ที่มี image
        media_with_image = Media.objects.create(
            post=post,
            image=SimpleUploadedFile(
                name="test_image.jpg",
                content=b"test data",
                content_type="image/jpeg"
            )
        )
        self.assertEqual(str(media_with_image), "media_images/test_image.jpg")

    # ไม่ใส่รูปภาพ   
    def test_media_str_without_image(self):
        post = self.hiring_posts[0]
        # สร้าง Media ที่ไม่มี image
        media_without_image = Media.objects.create(post=post)
        self.assertEqual(str(media_without_image), f"Media for Post ID: {post.id}")

        
        