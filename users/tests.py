from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
# Create your tests here.
class ProfileModelTest(TestCase):
    def test_profile_str(self):
        self.user = User.objects.create_user(username = 'minnie', password = 'minn9149')
        profile = Profile.objects.create(user=self.user, displayName="Minnie")

        # ตรวจสอบ __str__() คืนค่า username
        self.assertEqual(str(profile), "minnie")
        