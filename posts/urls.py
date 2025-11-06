from django.urls import path
from . import views  

app_name = 'posts' 

urlpatterns = [
    path('hiring/', views.hiring_page_view, name='hiring'),
    path('rental/', views.rental_page_view, name='rental'),
    path('post/<int:post_id>/', views.detail_post_view, name='detail_post'), 
]