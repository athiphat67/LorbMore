from django.test import SimpleTestCase
import os
import importlib
from unittest import mock

class DatabaseSettingsTest(SimpleTestCase):

    def test_database_settings_debug_true(self):
        """ทดสอบกรณี DEBUG=True -> ใช้ sqlite"""
        with mock.patch.dict(os.environ, {"DEBUG": "True"}):
            import my_project.settings as settings_module
            importlib.reload(settings_module)  # โหลดใหม่เพื่อให้ if else ทำงาน

            db_default = settings_module.DATABASES["default"]
            self.assertEqual(db_default["ENGINE"], "django.db.backends.sqlite3")
            self.assertEqual(db_default["NAME"], "db.sqlite3")

    def test_database_settings_debug_false(self):
        """ทดสอบกรณี DEBUG=False -> ใช้ DATABASE_URL"""
        with mock.patch.dict(os.environ, {
            "DEBUG": "False",
            "DATABASE_URL": "sqlite:///mytest.sqlite3"
        }):
            import my_project.settings as settings_module
            importlib.reload(settings_module)

            db_default = settings_module.DATABASES["default"]
            # ตรวจสอบว่าใช้ ENGINE จาก dj_database_url.parse
            self.assertEqual(db_default["ENGINE"], "django.db.backends.sqlite3")
            self.assertIn("NAME", db_default)
            self.assertTrue(db_default["NAME"].endswith("mytest.sqlite3"))
            
class StorageSettingsTest(SimpleTestCase):
    def test_storages_and_media_url_when_debug_false(self):
        """ทดสอบ STORAGES และ MEDIA_URL เมื่อ DEBUG=False"""
        env_vars = {
            "DEBUG": "False",
            "DATABASE_URL": "sqlite:///testdb.sqlite3",
            "AWS_LOCATION": "test-location",
            "AWS_S3_REGION_NAME": "ap-southeast-1",
            "AWS_S3_CUSTOM_DOMAIN": "test-bucket.s3.amazonaws.com",
        }

        with mock.patch.dict(os.environ, env_vars), \
             mock.patch("my_project.settings.AWS_LOCATION", "test-location"), \
             mock.patch("my_project.settings.AWS_S3_REGION_NAME", "ap-southeast-1"), \
             mock.patch("my_project.settings.AWS_S3_CUSTOM_DOMAIN", "test-bucket.s3.amazonaws.com"):

            import my_project.settings as settings_module
            importlib.reload(settings_module)

            # ตรวจสอบว่ามี STORAGES["default"]
            self.assertIn("default", settings_module.STORAGES)

            default_storage = settings_module.STORAGES["default"]
            self.assertEqual(
                default_storage["BACKEND"],
                "storages.backends.s3boto3.S3Boto3Storage"
            )

            options = default_storage["OPTIONS"]

            # ตรวจสอบค่าใน OPTIONS
            self.assertEqual(options["location"], "test-location")
            self.assertEqual(options["region_name"], "ap-southeast-1")
            self.assertEqual(
                options["object_parameters"]["CacheControl"], "max-age=86400"
            )

            # ตรวจสอบ MEDIA_URL
            expected_url = "https://test-bucket.s3.amazonaws.com/test-location/"
            self.assertEqual(settings_module.MEDIA_URL, expected_url)



        
        