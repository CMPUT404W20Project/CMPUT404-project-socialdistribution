from django.urls import path
from posts import views

urlpatterns = [
    # ex: /posts/
    path('', views.index, name='index'),
    # ex: /posts/5/
    path('<uuid:post_id>/', views.view_post, name='details'),
    path('<uuid:post_id>/comments/', views.postComments, name='comments'),
]