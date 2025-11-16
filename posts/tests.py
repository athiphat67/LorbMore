from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, RentalPost, HiringPost, Media, Skill, Category
from posts.forms import HiringPostForm, RentalPostForm
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
class PostIntegrationTestCase(TestCase):
    def setUp(self):
        
        # สร้าง Skill
        self.skills = Skill.objects.create(name = 'Photoshop')
        
        # สร้างผู้ใช้งาน
        self.user = User.objects.create_user(username = 'minnie', password = 'minn9149')
        
        # สร้าง Category
        self.categories = Category.objects.create(name = 'Photo')
        
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
            
            # เพิ่ม skill & catagories ลงใน post
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
        
    # hiring page โหลดสำเร็จ และจำกัดเพียง 6 โพสต์   
    def test_hiring_page_status_and_paginator(self):
        
        # สร้าง URL ของหน้า hiring จากชื่อ route
        url = reverse('posts:hiring')
        
        # จำลองการเข้าเว็บเหมือนผู้ใช้จริง โดยไม่ต้องรันเซิร์ฟเวอร์
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('hiring_items', response.context)
    
        # หน้า hiring page จะต้องมี post มากสุด 6 โพสต์
        # หน้าแรกมี 6 โพสต์
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

    # hiring page มีโพสต์ที่ข้อมูลตรงกับ formatted_item
    def test_hiring_items_format(self):
        url = reverse('posts:hiring')
        response = self.client.get(url)
        formatted_item = response.context['hiring_items'][0]
    
        # ตรวจสอบว่า expected_keys ที่เรากำหนดตรงกับ formatted_item 
        expected_keys = ['id', 'image_url', 'title', 'reviews', 'rating', 'price_detail']
        for key in expected_keys:
            self.assertIn(key, formatted_item)
        
        # ตรวจสอบว่า price_detail มี "/วัน" สำหรับ RentalPost
        self.assertIn('เริ่มต้น', formatted_item['price_detail'])    
    
    # rental page โหลดสำเร็จ และจำกัดเพียง 6 โพสต์   
    def test_rental_page_status_and_paginator(self):
        url = reverse('posts:rental')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rental_items', response.context)
    
        # หน้า rental page จะต้องมี post มากสุด 6 โพสต์
        # หน้าแรกมี 6 โพสต์
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj'].object_list), 6)

    
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
    
    # ข้อมูลของโพสต์ hiring page ครบถ้วน 
    def test_detail_post_hiring(self):
        post = self.hiring_posts[0]
        
        # ใช้ reverse() เพื่อสร้าง URL สำหรับหน้าแสดงรายละเอียดโพสต์ (detail_post) 
        # ส่ง post.id ใส่ใน URL pattern
        url = reverse('posts:detail_post', args=[post.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
        # ตรวจสอบว่าส่ง is_hiring ใน context ไปยัง template
        self.assertTrue(response.context['is_hiring'])
    
        # ตรวจสอบ media 
        # ดึง media ที่ผูกกับโพสต์
        media = list(response.context['media'])
        self.assertEqual(len(media), 4)
        
        # ตรวจสอบข้อมูล post
        post = response.context['post']
        self.assertEqual(post.id, self.hiring_posts[0].id)
        self.assertEqual(post.title, self.hiring_posts[0].title)
        self.assertEqual(post.budgetMin, self.hiring_posts[0].budgetMin)
        self.assertEqual(post.budgetMax, self.hiring_posts[0].budgetMax)
    
    # ข้อมูลของโพสต์ rental page ครบถ้วน     
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
        
    # ตรวจว่าการแปลง object ของแต่ละโมเดลเป็นข้อความ (__str__) ทำงานถูกต้องตามที่ตั้งใจไว้
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
        
        # สร้าง Media 
        media_with_image = Media.objects.create(
            post=post,
            # มีรูปภาพจริงๆ จำลองด้วย SimpleUploadedFile
            image=SimpleUploadedFile(
                name="test_image.jpg",
                content=b"test data",
                content_type="image/jpeg"
            )
        )
        # self.assertIn("test_image", media_with_image.image.name)
        self.assertTrue(str(media_with_image), "media_images/test_image.jpg")

    # ไม่ใส่รูปภาพ   
    def test_media_str_without_image(self):
        post = self.hiring_posts[0]
        
        # สร้าง Media ที่ไม่มี image
        media_without_image = Media.objects.create(post=post)
        self.assertEqual(str(media_without_image), f"Media for Post ID: {post.id}")

# class แยกสำหรับทดสอบเวลาสร้างโพสต์     
class PostCreationTests(TestCase):
    def setUp(self):
        # สร้าง user
        self.user = User.objects.create_user(username="minnie", password="123456")
        self.client = Client()
        self.client.force_login(self.user)

        # สร้าง Category และ Skill 
        self.category = Category.objects.create(name='Photo')
        self.skill = Skill.objects.create(name='Photoshop')

    # ตรวจสอบหน้า create post สามารถโหลดได้สำเร็จ
    def test_createpost_view_status_and_template(self):
        url = reverse('posts:createposts') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/createposts.html')

    # ตรวจสอบหน้า create hiring post แสดงแบบฟอร์มถูกหรือไม่
    def test_create_hiring_post_get(self):
        # จำลองผู้ใช้ที่ล็อกอินแล้ว
        self.client.force_login(self.user)
        url = reverse('posts:create_hiring')
        
        # จำลองการเปิดหน้าเว็บ
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # ยืนยันเปิดหน้า hiring และใช้ form ที่ถูกต้อง
        self.assertContains(response, 'Create your hiring post')
        self.assertIsInstance(response.context['form'], HiringPostForm)

    # ตรวจสอบหน้า create rental post แสดงแบบฟอร์มถูกหรือไม่
    def test_create_rental_post_get(self):
        self.client.force_login(self.user)
        url = reverse('posts:create_rental')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Create your rental post')
        self.assertIsInstance(response.context['form'], RentalPostForm)
    
    # ตรวจสอบการสร้างโพสต์ hiring ในกรณีที่ข้อมูลครบ
    def test_create_hiring_post__valid_post(self):
        url = reverse('posts:create_hiring')
        
        # สร้างข้อมูลทดสอบและรูปภาพ
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"test image content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': 'Test Hiring',
            'description': 'Test description',
            'categories': [self.category.id],
            'skills': [self.skill.id],
            'budgetMin': 1000,
            'budgetMax': 2000,
            'images': [test_image],
        }
        
        # จำลองการกรอกฟอร์มในหน้าเว็บจริง โดยมีทั้ง data และ files รูป
        response = self.client.post(url, data, FILES={"images": [test_image]})
        
        # สร้างโพสต์สำเร็จและระบบเปลี่ยนหน้าให้ถูกต้อง
        self.assertEqual(response.status_code, 302)
        
        # ยืนยันว่ามีโพสต์จริง ไม่เป็น none และข้อมูลถูกบันทึกจริงและผูกกับผู้ใช้ถูกคน
        post = HiringPost.objects.get(title='Test Hiring')
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.user)

        # ดึง media และเช็คจำนวนรูป, ยืนยันว่าชื่อไฟล์ของรูปตรงกับรูปที่เราอัปโหลด
        media = Media.objects.filter(post=post)
        self.assertEqual(media.count(), 1)
        self.assertIn("test_image", media.first().image.name)
    
    # ตรวจสอบการสร้างโพสต์ hiring ในกรณีที่ข้อมูลไม่ครบ (title) 
    def test_create_hiring_post__invalid_post(self):
        url = reverse('posts:create_hiring')
        
        # สร้างข้อมูลทดสอบและรูปภาพ
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"test image content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': '',  # invalid
            'description': 'Test description',
            'categories': [self.category.id],
            'skills': [self.skill.id],
            'budgetMin': 1000,
            'budgetMax': 2000,
        }
        
        response = self.client.post(url, data)
        
        # ระบบ render หน้าเดิม แทนการ redirect
        self.assertEqual(response.status_code, 200)
        
        # ตรวจว่าหน้า template ที่ใช้คือหน้าเดิมของฟอร์ม
        self.assertTemplateUsed(response, "pages/create_hiring.html")

    # ตรวจสอบการสร้างโพสต์ rental ในกรณีที่ข้อมูลครบ
    def test_create_rental_post_valid_post(self):
        url = reverse('posts:create_rental')
        
         # สร้างข้อมูลทดสอบและรูปภาพ
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"test image content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': 'Test Rental',
            'description': 'Test rental description',
            'categories': [self.category.id],
            'skills': [],  # rental ไม่มี skills
            'pricePerDay': 100,
            'deposit': 0,
            'images': [test_image],
        }
        
        
        response = self.client.post(url, data, FILES={"images": [test_image]})
        self.assertEqual(response.status_code, 302) 

        # ยืนยันว่ามีโพตส์จริง ไม่เป็น none และข้อมูลถูกบันทึกจริงและผูกกับผู้ใช้ถูกคน 
        post = RentalPost.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.author, self.user)

        media = Media.objects.filter(post=post)
        self.assertEqual(media.count(), 1)
        self.assertIn("test_image", media.first().image.name)
        
    # ตรวจสอบการสร้างโพสต์ rental ในกรณีที่ข้อมูลไม่ครบ
    def test_create_rental_post__invalid_post(self):
        url = reverse('posts:create_rental')
        
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"test image content",
            content_type="image/jpeg"
        )
        
        data = {
            'title': '',  # invalid
            'description': 'Test rental description',
            'categories': [self.category.id],
            'skills': [],
            'pricePerDay': 100,
            'images': [test_image],
        }
        
        response = self.client.post(url, data, FILES={"images": [test_image]})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/create_rental.html")

    # ตรวจสอบว่า login required redirect
    def test_login_required_redirect(self):
        self.client.logout()
        
        # สร้างหน้า create hiring กับ rental
        url_hiring = reverse('posts:create_hiring')
        url_rental = reverse('posts:create_rental')
        
        # จำลองผู้ใช้ถ้าไม่ log in
        response_hiring = self.client.get(url_hiring)
        response_rental = self.client.get(url_rental)
        
        # ไม่สามารถเข้าหน้านั้นได้
        self.assertEqual(response_hiring.status_code, 302)
        self.assertIn('/accounts/login/', response_hiring.url)
        self.assertEqual(response_rental.status_code, 302)
        self.assertIn('/accounts/login/', response_rental.url)
    
    # ตรวจสอบกรณีมีรูป
    def test_create_hiring_post_with_image(self):
        url = reverse('posts:create_hiring')

        # สร้างข้อมูลทดสอบและรูปภาพ
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"dummy_image_content",
            content_type="image/jpeg"
        )

        data = {
            'title': 'Test Hiring',
            'description': 'Test description',
            'categories': [self.category.id],
            'skills': [self.skill.id],
            'budgetMin': 1000,
            'budgetMax': 2000,
            'images': [test_image],

        }

        response = self.client.post(url, data, FILES={'images': [test_image]})


        self.assertEqual(response.status_code, 302)
        post = HiringPost.objects.get(title='Test Hiring')
        self.assertEqual(post.author, self.user)

        # ดึง media และเช็คจำนวนรูป, ยืนยันว่าชื่อไฟล์ของรูปตรงกับรูปที่เราอัปโหลด
        media = Media.objects.filter(post=post)
        self.assertEqual(media.count(), 1)
        self.assertIn("test_image",media[0].image.name)
        
    # ตรวจสอบกรณีไม่มีรูป    
    def test_create_rental_post_without_image(self):
        url = reverse('posts:create_rental')

        data = {
            'title': 'Test Rental No Image',
            'description': 'Rental post without image',
            'categories': [self.category.id],
            'skills': [],
            'pricePerDay': 100,
            'deposit': 0
        }

        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        post = RentalPost.objects.get(title='Test Rental No Image')
        self.assertEqual(post.author, self.user)

        # มีจำนวนรูป 0
        media_objects = Media.objects.filter(post=post)
        self.assertEqual(media_objects.count(), 0)