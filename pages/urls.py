from django.urls import path
from . import views  

urlpatterns = [
    path('about/', views.about_page_view, name='about'),
    path('', views.home_page_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('contact/', views.contact_view, name='contact'),
    

]
