from django.urls import path
from . import views  

urlpatterns = [
    path('about/', views.about_page_view, name='about'),
    path('', views.home_page_view, name='home'),
]