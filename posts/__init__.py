from django.test import SimpleTestCase
import importlib

class WSGITestCase(SimpleTestCase):
    def test_wsgi_application_loads(self):
        wsgi = importlib.import_module("my_project.wsgi")
        self.assertIsNotNone(wsgi.application)