from django.urls import path
from . import views  

urlpatterns = [
    path('about/', views.about_page_view, name='about'),
    path('', views.home_page_view, name='home'),
    path('hiring/', views.hiring_page_view, name='hiring'),
    path('rental', views.rental_page_view, name='rental'),

    #เก็บ userเป็นตัวเลขลำดับ
    path('post/<int:post_id>/', views.detail_post_view, name='detail_post'), 
]
