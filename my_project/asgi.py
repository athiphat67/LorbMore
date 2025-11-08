"""
ASGI config for my_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# Unit tests รันผ่าน WSGI/manage.py test ไม่ได้ใช้ ASGI server → get_asgi_application() ไม่ถูก execute
import os # pragma: no cover

from django.core.asgi import get_asgi_application # pragma: no cover

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings') # pragma: no cover

application = get_asgi_application() # pragma: no cover
