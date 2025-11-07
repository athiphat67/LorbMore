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
            
        Media.objects.create(post=post, image=f"media_images/hiring{i}_1.jpg")
        
        for i in range(5):
            post = RentalPost.objects.create(
                author = user,
                title = f"post {i}: ให้เช่ายืมกล้องถ่ายรูป",
                pricePerDay = 100,
                deposit = 2,
            )
            
        Media.objects.create(post=post, image=f"media_images/hiring{i}_1.jpg")
        
    def test_about_page_status(self):
        urls = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about.html")

    def test_home_page_status_context_and_template(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

        self.assertIn("hiring_items", response.context)
        self.assertIn("rental_items", response.context)

        # จำกัด 3 ตัวล่าสุด
        self.assertEqual(len(response.context["hiring_items"]), 3)
        self.assertEqual(len(response.context["rental_items"]), 3)
        
    def test_home_page_latest_items_order(self):
        url = reverse("home")
        response = self.client.get(url)

        hiring_items = response.context["hiring_items"]
        rental_items = response.context["rental_items"]

        # ตัวล่าสุดควรเป็น index 4 (id มากสุด)
        self.assertTrue(hiring_items[0]["title"].endswith("4"))
        self.assertTrue(rental_items[0]["title"].endswith("4"))
    
    # ทดสอบ prefetch media  
    def test_home_page_prefetch_media(self):
        url = reverse("home")
        response = self.client.get(url)

        hiring_items = response.context["hiring_items"]
        rental_items = response.context["rental_items"]

        for item in hiring_items:
            self.assertIn("images", item)
            self.assertEqual(len(item["images"]), 2)

        for item in rental_items:
            self.assertIn("images", item)
            self.assertEqual(len(item["images"]), 2)
    
    # ทดสอบ _format_post_data แยกเดี่ยว (unit test)
    def test_format_post_data_function(self):
        post = HiringPost.objects.first()
        post.images = list(post.media.all())  # จำลอง prefetch
        formatted = _format_post_data(post)

        self.assertEqual(formatted["id"], post.id)
        self.assertIn("title", formatted)
        self.assertIn("type", formatted)
        self.assertEqual(len(formatted["images"]), 2)
         