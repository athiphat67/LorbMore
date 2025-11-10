from django.urls import path
from . import views  

app_name = 'posts' 

urlpatterns = [
    path('hiring/', views.hiring_page_view, name='hiring'),
    path('rental/', views.rental_page_view, name='rental'),
    path('post/<int:post_id>/', views.detail_post_view, name='detail_post'), 
    path('create/', views.createpost, name='createposts'), 
    path('create/hiring/', views.create_hiring_view, name='create_hiring'),
    path('create/rental/', views.create_rental_view, name='create_rental'),
]