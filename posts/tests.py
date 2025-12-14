from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, RentalPost, HiringPost, Media, Skill, Category, Review
from posts.forms import HiringPostForm, RentalPostForm, ReviewForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.http import urlencode
from django.db.models import Q

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
        expected_keys = ['id', 'image_url', 'title', 'count_reviews', 'avg_rating', 'price_detail']
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
        expected_keys = ['id', 'image_url', 'title', 'count_reviews', 'avg_rating', 'price_detail']
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
        review = Review.objects.create( post=post, author=self.user, rating=4, comment="Good!")

        self.assertEqual(str(post), "Base Post")
        self.assertEqual(str(skill), "TestSkill")
        self.assertEqual(str(category), "TestCat")
        self.assertEqual(str(rental), "[Rental] Rent")
        self.assertEqual(str(hiring), "[Hiring] Hire")
        self.assertEqual(str(media), f"Media for Post ID: {rental.id}")
        self.assertEqual(str(review), f"Rating 4 on {post.title} by {self.user.username}")
    
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
        self.user = User.objects.create_user(
            username="minnie",
            email="minnie@dome.tu.ac.th",
            password="123456"
        )
        
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
        self.assertContains(response, 'Create hiring post')
        self.assertIsInstance(response.context['form'], HiringPostForm)

    # ตรวจสอบหน้า create rental post แสดงแบบฟอร์มถูกหรือไม่
    def test_create_rental_post_get(self):
        self.client.force_login(self.user)
        url = reverse('posts:create_rental')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Create rental post')
        self.assertIsInstance(response.context['form'], RentalPostForm)
    
    # ตรวจสอบการสร้างโพสต์ hiring ในกรณีที่ข้อมูลครบ
    def test_create_hiring_post__valid_post(self):
        url = reverse('posts:create_hiring')
        
        self.client.login(username="minnie", password="123456")
        
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
            'images': [test_image]
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
        
        self.client.login(username="minnie", password="123456")
        
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
        self.assertTemplateUsed(response, 'pages/create_hiring.html')

    # ตรวจสอบการสร้างโพสต์ rental ในกรณีที่ข้อมูลครบ
    def test_create_rental_post_valid_post(self):
        url = reverse('posts:create_rental')
    
        self.client.login(username="minnie", password="123456")
        
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
        
        self.client.login(username="minnie", password="123456")
        
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
        self.assertTemplateUsed(response, 'pages/create_rental.html')

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
        
        # login ก่อน
        self.client.login(username="minnie", password="123456")

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
            'images': [test_image]
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
        
        self.client.login(username="minnie", password="123456")
        
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
        
class PostViewTests(TestCase):
    def setUp(self):
        # สร้าง user 2 คน
        self.owner = User.objects.create_user(username="owner", password="123456", email="owner.on@dome.tu.ac.th")
        self.other = User.objects.create_user(username="other", password="1234567")
        
        # Category และ Skill
        self.category = Category.objects.create(name="Test Category")
        self.skill = Skill.objects.create(name="Python")
        
        # สร้างโพสต์
        # rental post
        self.rental = RentalPost.objects.create(
            author=self.owner,
            title="Camera Rent",
            description="Rent description",
            pricePerDay=500,
            deposit=2,
        )
        self.rental.categories.add(self.category)

        # hiring post
        self.hiring = HiringPost.objects.create(
            author=self.owner,
            title="Hiring Develop",
            description="Hire description",
            budgetMin=1000,
            budgetMax=2000,
        )
        self.hiring.skills.add(self.skill)
        
        self.url_mypost = reverse("posts:mypost")
        self.url = reverse("posts:delete_post", args=[self.rental.id])
        self.rental_url_detail = reverse("posts:detail_post", args=[self.rental.id])
        self.hiring_url_detail = reverse("posts:detail_post", args=[self.hiring.id])
        self.rental_url_edit = reverse("posts:edit_post", args=[self.rental.id])
        self.hiring_url_edit = reverse("posts:edit_post", args=[self.hiring.id])
        
    def test_my_post_view_status_and_template(self):
        # ตรวจสอบว่า user login แล้วสามารถเข้าดูหน้าได้
        self.client.login(username="owner", password="123456")
        response = self.client.get(self.url_mypost)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/mypost.html")
        
    def test_my_post_view_returns_correct_items(self):
        # login user ที่มีโพสต์
        self.client.login(username="owner", password="123456")

        # request view
        response = self.client.get(self.url_mypost)
        self.assertEqual(response.status_code, 200)  # ต้อง 200

        # ดึง context
        items = response.context["mypost_items"]

        # ตรวจสอบจำนวนโพสต์
        self.assertEqual(len(items), 2)

        # ตรวจสอบลำดับ id จากเก่า → ใหม่
        item_ids = [item["id"] for item in items]
        self.assertEqual(item_ids, sorted(item_ids))
        
    def test_my_post_view_can_create(self):
        # ตรวขสอบสิทธิ์คนที่สามารถสร้างโพสต์ได้
        # user ปกติ email @dome.tu.ac.th = True
        self.client.login(username="owner", password="123456", email="owner.on@dome.tu.ac.th")
        response = self.client.get(self.url_mypost)
        self.assertTrue(response.context["can_create"])

        # user ปกติ email ปกติ → can_create = False
        self.client.login(username="other", password="1234567")
        response = self.client.get(self.url_mypost)
        self.assertFalse(response.context["can_create"])

        # superuser → can_create = True
        admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@admin.com")
        self.client.login(username="admin", password="admin123")
        response = self.client.get(self.url_mypost)
        self.assertTrue(response.context["can_create"])
    
    # ------------
    # Delete_post   
    # ------------    
    def test_not_logged_in(self):
        # กรณีผู้ใช้ไม่ได้ login => redirect ไปหน้า login
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url) # string ของ URL หลัง redirect
        
    def test_delete_post_owner(self):
        # กรณีเจ้าของลบโพสต์ => redirect ไปหน้า mypost
        self.client.login(username="owner", password="123456")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:mypost"))
        
        # โพสต์ต้องหายไปแล้ว
        self.assertFalse(Post.objects.filter(id=self.rental.id).exists())
    
    def test_delete_post_other_user(self):
        # กรณีคนที่ไม่ใช่เจ้าของลบโพสต์ => โพสต์ยังอยู่
        self.client.login(username="other", password="1234567")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.rental_url_detail)
        
        # โพสต์ต้องยังอยู่
        self.assertTrue(Post.objects.filter(id=self.rental.id).exists())
        
    # ------------
    # Edit_post   
    # ------------
    def test_edit_post_other_user(self):
        # กรณีคนที่ไม่ใช่เจ้าของแก้ไขโพสต์ => redirect ไป detail_post
        self.client.login(username="other", password="1234567")
        response = self.client.get(self.rental_url_edit)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.rental_url_detail)
    
    def test_rental_edit_form(self):
        # กรณีถูกฟอร์ม_GET RentalPost
        self.client.login(username="owner", password="123456")
        response = self.client.get(self.rental_url_edit)

        self.assertEqual(response.status_code, 200)
        
        # ยืนยันว่า form ที่ให้ user ใช้แก้ไขหรือสร้างเป็น rental post ถูกต้อง
        self.assertTemplateUsed(response, "pages/create_rental.html")
        self.assertIsInstance(response.context["form"], RentalPostForm)
        
        # ยืนยันว่าหน้านี้คือแก้ไข rental post
        self.assertTrue(response.context["is_edit"])

    def test_hiring_edit_form(self):
        # กรณีถูกฟอร์ม_GET HiringPost
        self.client.login(username="owner", password="123456")
        response = self.client.get(self.hiring_url_edit)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/create_hiring.html")
        self.assertIsInstance(response.context["form"], HiringPostForm)
        self.assertTrue(response.context["is_edit"])

    def test_rental_post_update_with_media(self):
        # สามารถอัปเดตรูปกับข้อมูลสำเร็จ (RentalPost)
        self.client.login(username="owner", password="123456")

        # สร้างข้อมูลทดสอบและรูปภาพ
        test_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"dummy_image_content",
            content_type="image/jpeg"
        )

        # อับเดตข้อมูล
        response = self.client.post(
            self.rental_url_edit,
            {
                "title": "Updated Camera",         
                "description": "Updated description",     
                "pricePerDay": 650,
                "deposit": 2,
                "categories": [self.category.id],
                "images": test_image,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.rental_url_detail)
        
        # เช็คว่าข้อมูลอัปเดตตรงกับข้อมูลหรือไม่
        rental = RentalPost.objects.get(id=self.rental.id)
        self.assertEqual(rental.title, "Updated Camera")
        self.assertEqual(rental.pricePerDay, 650)
        self.assertEqual(rental.description, "Updated description")
        self.assertEqual(rental.categories.count(), 1)
        self.assertEqual(Media.objects.filter(post=rental).count(), 1)

    def test_hiring_post_update(self):
        # สามารถอัปเดตรูปและข้อมูลสำเร็จ (HiringPost)
        self.client.login(username="owner", password="123456")

        # อัปเดตราคา
        response = self.client.post(
            self.hiring_url_edit,
            {
                "title": "Updated Hiring",
                "description": "Updated Hiring Desc",
                "budgetMin": 2000,
                "budgetMax": 3000,
                "skills": [self.skill.id],
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.hiring_url_detail)

        # เช็คว่าข้อมูลอัปเดตตรงกับข้อมูลหรือไม่
        hiring = HiringPost.objects.get(id=self.hiring.id)
        self.assertEqual(hiring.title, "Updated Hiring")
        self.assertEqual(hiring.description, "Updated Hiring Desc")
        self.assertEqual(hiring.budgetMin, 2000)
        self.assertEqual(hiring.budgetMax, 3000)
        self.assertEqual(hiring.skills.count(), 1)

    def test_edit_post_not_rental_or_hiring(self):
        # กรณีอื่นๆ ไม่ใช่ hiring or rental => กลับมา mypost
        # สร้างโพสต์ที่ไม่ใช่ rental หรือ hiring
        base_post = Post.objects.create(
            author=self.owner,
            title="Not hiring/rental Post",
            description="Post description",
            type=None,
        )

        url = reverse("posts:edit_post", args=[base_post.id])

        self.client.login(username="owner", password="123456")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:mypost"))
        
class ReviewViewTests(TestCase):

    def setUp(self):
        # User 2 คน
        self.owner = User.objects.create_user(username="owner", password="123456")
        self.reviewer = User.objects.create_user(username="reviewer", password="1234567")

        # Post
        self.post = Post.objects.create(
            author=self.owner,
            title="Test Post",
            description="description"
        )

        self.url = reverse("posts:add_review", args=[self.post.id])

    def test_not_logged_in(self):
        # กรณีผู้ใช้ไม่ได้ login => redirect ไปหน้า login
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_owner_cannot_review_own_post(self):
        # เจ้าของโพสต์ไม่สามารถรีวิวตัวเอง
        self.client.login(username="owner", password="123456")
        response = self.client.post(self.url, {"rating": 5, "comment": "Nice!"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:detail_post", args=[self.post.id]))

        # ไม่มี review ถูกสร้าง
        self.assertEqual(Review.objects.count(), 0)

    def test_valid_review_created(self):
        self.client.login(username="reviewer", password="1234567")

        response = self.client.post(self.url, {
            "rating": 4,
            "comment": "Good!"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:detail_post", args=[self.post.id]))

        # Review ถูกสร้าง
        review = Review.objects.first()
        # ตรวจสอบว่า review ไม่ใช่ None
        self.assertIsNotNone(review)
        # ตรวจสอบว่า review ถูกผูกกับโพสต์ที่ถูกต้อง
        self.assertEqual(review.post, self.post)
        # ตรวจสอบว่า review ผู้สร้างคือผู้ใช้ที่ login
        self.assertEqual(review.author, self.reviewer)
        # ตรวจสอบว่า ข้อมูล rating และ comment ตรงตามที่ส่งมา
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Good!")

    # def test_invalid_review_not_created(self):
    #     self.client.login(username="reviewer", password="1234567")

    #     # rating ไม่ส่ง → form ไม่ valid
    #     response = self.client.post(self.url, {
    #         "comment": "Missing rating"
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, reverse("posts:detail_post", args=[self.post.id]))
    #     self.assertEqual(Review.objects.count(), 0)

    def test_get_request_redirect(self):
        # กรณีทั้ง valid or invalid review => redirect detail post
        self.client.login(username="reviewer", password="1234567")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:detail_post", args=[self.post.id]))
        
    # def test_rating_out_of_range(self):
    #     # ให้ rating มากกว่า 5 คะแนน
    #     self.client.login(username="reviewer", password="1234567")
        
    #     response = self.client.post(self.url, {
    #         "rating": 10,
    #         "comment": "Too high rating"
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, reverse("posts:detail_post", args=[self.post.id]))
    #     self.assertEqual(Review.objects.count(), 0)

        
class BookingViewTests(TestCase):

    def setUp(self):
        # ผู้ใช้เจ้าของโพสต์
        self.user = User.objects.create_user(username="user", password="12345")
        
        # ผู้ใช้ที่จะใช้ทดสอบการจอง
        self.test = User.objects.create_user(username="test", password="123456")

        # Category และ Skill
        self.category = Category.objects.create(name="Test Category")
        self.skill = Skill.objects.create(name="Python")
        
        # สร้างโพสต์
        # rental post
        self.rental = RentalPost.objects.create(
            author=self.user,
            title="Camera Rent",
            description="Rent desc",
            pricePerDay=500,
            deposit=100,
        )
        self.rental.categories.add(self.category)

        # hiring post
        self.hiring = HiringPost.objects.create(
            author=self.user,
            title="Hiring Dev",
            description="Hire desc",
            budgetMin=1000,
            budgetMax=2000,
        )
        self.hiring.skills.add(self.skill)

        self.toggle_url_rental = reverse("posts:toggle_booking", args=[self.rental.id])
        self.toggle_url_hiring = reverse("posts:toggle_booking", args=[self.hiring.id])
        self.my_booking_url = reverse("posts:mybooking")

    def test_not_logged_in(self):
        # กรณีผู้ใช้ไม่ได้ login => redirect ไปหน้า login
        response = self.client.get(self.toggle_url_rental)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    
    def test_toggle_add_booking(self):
        # toggle: ยังไม่จอง → จองได้
        self.client.login(username="test", password="123456")

        response = self.client.get(self.toggle_url_rental, HTTP_REFERER="/previous")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/previous")

        # เช็คว่าผู้ใช้ถูกเพิ่มเข้า bookings ของ rental post จริง
        self.assertTrue(self.rental.bookings.filter(id=self.test.id).exists())

    def test_toggle_remove_booking(self):
        # toggle: จองแล้ว → ยกเลิกจอง
        self.client.login(username="test", password="123456")
        self.rental.bookings.add(self.test)

        response = self.client.get(self.toggle_url_rental, HTTP_REFERER="/previous")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/previous")

        # booking ถูกลบ และ redirect กลับ
        self.assertFalse(self.rental.bookings.filter(id=self.test.id).exists())

    
    def test_toggle_no_referer_redirect_default(self):
        # Redirect กลับไปหน้าเดิมที่ user กดมา
        self.client.login(username="test", password="123456")

        response = self.client.get(self.toggle_url_hiring)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("posts:hiring"))
    
    def test_my_booking_view_has_items(self):
        # มีการจอง และแสดงโพสต์ที่จองถูกต้อง
        # user จอง rental/hiring
        self.rental.bookings.add(self.user)
        self.hiring.bookings.add(self.user)

        self.client.login(username="user", password="12345")
        response = self.client.get(self.my_booking_url)
        
        items = response.context["booking_items"]

        # ต้องได้ 2 โพสต์
        self.assertEqual(len(items), 2)

        # ตรวจสอบว่ามี id ของ rental และ hiring
        returned_ids = [item["id"] for item in items]
        self.assertIn(self.rental.id, returned_ids)
        self.assertIn(self.hiring.id, returned_ids)
        
    def test_my_booking_view_order_by_newest(self):
        # โพสต์เรียงจากเก่าไปใหม่
        # เพิ่ม booking
        self.rental.bookings.add(self.user)
        self.hiring.bookings.add(self.user)

        self.client.login(username="user", password="12345")
        response = self.client.get(self.my_booking_url)
        items = response.context["booking_items"]

        # ตรวจสอบว่าตามลำดับ id จากมาก → น้อย
        item_ids = [item["id"] for item in items]
        self.assertEqual(item_ids, sorted(item_ids, reverse=True))

    def test_my_booking_view_media_attached(self):
        # my_booking_view รวม media ถูกต้อง 
        self.client.login(username="test", password="123456")

        # ทำ media ให้ rental post
        Media.objects.create(post=self.rental, image="test1.jpg")
        Media.objects.create(post=self.rental, image="test2.jpg")

        self.rental.bookings.add(self.test)

        response = self.client.get(self.my_booking_url)
        items = response.context["booking_items"]

        # ต้องมีเพียงโพสต์เดียว
        self.assertEqual(len(items), 1)

        rental_item = items[0]

        # ต้องมี key image_url
        self.assertIn("image_url", rental_item)

        # ต้องเป็นรูป test1 หรือ test2
        self.assertTrue(
            rental_item["image_url"].endswith("test1.jpg")
            or rental_item["image_url"].endswith("test2.jpg")
        )
        
class SearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="123456"
        )

        self.search_url = reverse("posts:search")

        # Skill / Category
        self.skill = Skill.objects.create(name="Photography")
        self.category = Category.objects.create(name="Camera")

        # Hiring post
        self.hiring_post = HiringPost.objects.create(
            author=self.user,
            title="Photographer for wedding",
            description="Looking for wedding photographer",
            budgetMin=100,
            budgetMax=500,
        )
        self.hiring_post.skills.add(self.skill)

        # Rental post
        self.rental_post = RentalPost.objects.create(
            author=self.user,
            title="Camera for rent",
            description="Canon camera rental",
            pricePerDay=300,
        )
        self.rental_post.categories.add(self.category)
    
    def test_search_only_hiring_post(self):
        response = self.client.get(self.search_url, {"q": "Photographer"})

        self.assertEqual(response.status_code, 200)

        items = response.context["search_items"]

        # เจอ 1 รายการ
        self.assertEqual(len(items), 1)

        # เป็น hiring post
        self.assertEqual(items[0]["id"], self.hiring_post.id)
    
    def test_search_only_rental_post(self):
        response = self.client.get(self.search_url, {"q": "Camera"})

        self.assertEqual(response.status_code, 200)

        items = response.context["search_items"]

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], self.rental_post.id)
        
    def test_search_hiring_and_rental_sorted_by_id_desc(self):
        new_rental = RentalPost.objects.create(
            author=self.user,
            title="Photographer equipment",
            description="New post",
            pricePerDay=350,
        )
        
        response = self.client.get(self.search_url, {"q": "Photographer"})

        items = response.context["search_items"]

        self.assertEqual(len(items), 2)

        # เรียงจาก id มาก → น้อย
        self.assertGreater(items[0]["id"], items[1]["id"])