"""socialdistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from profiles import views as profiles_views
from socialdistribution import views as socialdistribution_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', profiles_views.register, name="register"),

    path('', lambda request: redirect('stream/', permanent=True)),
    path('stream/', include('posts.urls')),
    path('new_post/', include('profiles.urls')),
    path('editprofile/', profiles_views.edit_profile, name='editprofile'),
    path('viewprofile/', profiles_views.view_profile, name='viewprofile'),
    path(
        'author/<uuid:author_id>/profile', profiles_views.view_author_profile, name='view_author_profile'
    ),
    path('friends/', profiles_views.my_friends, name='my_friends'),
    path('friends/add', profiles_views.search_friends, name='search_friends'),
    path('friends/friend_requests', profiles_views.my_friend_requests, name='my_friend_requests'),
    path('friends/friend_following', profiles_views.my_friend_following, name='my_friend_following'),
    path('friends/accept/<uuid:friend_id_to_accept>/', profiles_views.accept_friend, name='accept_friend'),
    path('friends/reject/<uuid:friend_id_to_reject>/', profiles_views.reject_friend, name='reject_friend'),
    path('api/', include('api.urls')),
    path('404/', socialdistribution_views.error_404, name='error_404'),
    path('403/', socialdistribution_views.error_403, name='error_403'),
    path('500/', socialdistribution_views.error_500, name='error_500'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
