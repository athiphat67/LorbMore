from django.urls import path
from . import views  

urlpatterns = [
    path('', views.about_page_view, name='about'),
]