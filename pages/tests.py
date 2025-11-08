from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from posts.models import HiringPost, RentalPost, Media
from posts.views import _format_post_data

# Create your tests here.
class PagesViewTests(TestCase):
    def setUp(selt):
        user = User.object.create_user(username = 'minnie', password = 'minn9149')
        
        #สร้าง hiring post 5 โพสต์
        for i in range(5):
            post = HiringPost.objects.create(
                author = user,
                title = f"post {i}: รับจ้างถ่ายรูปปริญญา",
                budgetMin = 600,
                budgetMax = 1500,
            )
            for j in range(1, 3):
                Media.objects.create(post=post, image=f"media_images/hiring{i}_{j}.jpg")
        
        for i in range(5):
            post = RentalPost.objects.create(
                author = user,
                title = f"post {i}: ให้เช่ายืมกล้องถ่ายรูป",
                pricePerDay = 100,
                deposit = 2,
            )
            for j in range(1, 3):
                Media.objects.create(post=post, image=f"media_images/rental{i}_{j}.jpg")
            
    def test_about_page_status(self):
        urls = reverse("about")
        response = self.client.get(url)
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
            post_obj = HiringPost.objects.get(id=item["id"])
            expected_image = post_obj.media.first().image.url
            self.assertEqual(item["image_url"], expected_image)

        for item in rental_items:
            post_obj = RentalPost.objects.get(id=item["id"])
            expected_image = post_obj.media.first().image.url
            self.assertEqual(item["image_url"], expected_image)
            
        # ตรวจว่า index 0 = โพสต์ล่าสุด
        hiring_ids = [item["id"] for item in hiring_items]
        rental_ids = [item["id"] for item in rental_items]
        self.assertEqual(hiring_ids, sorted(hiring_ids, reverse=True))
        self.assertEqual(rental_ids, sorted(rental_ids, reverse=True))
    
    # ทดสอบ _format_post_data แยกเดี่ยว (unit test)
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
        self.assertEqual(len(formatted["images"]), 2)

         