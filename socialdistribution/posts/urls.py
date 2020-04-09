from django.urls import path
from posts import views

urlpatterns = [
    # ex: /stream/
    path('', views.index, name='index'),
    path('old', views.old_stream, name="old-stream"),
    # ex: /stream/5/
    path('<uuid:post_id>/', views.view_post, name='details'),
    path('<uuid:post_id>/edit', views.edit_post, name='editpost'),
    path('<uuid:post_id>/comments/', views.post_comments, name='comments'),
]
