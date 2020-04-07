from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

# Decorated url instead of view as csrf_exempt
# https://stackoverflow.com/a/60252189

urlpatterns = [
    path(
        "posts",
        csrf_exempt(views.posts),
        name="api_get_all_public_posts"),
    path(
        "posts/<uuid:post_id>",
        csrf_exempt(views.single_post),
        name="api_get_single_post"),
    path(
        "posts/<uuid:post_id>/comments",
        csrf_exempt(views.post_comments),
        name="api_post_comments"),
    path(
        "author/posts",
        csrf_exempt(views.author_posts),
        name="api_get_author_posts"),
    path(
        "author/<uuid:author_id>",
        csrf_exempt(views.author_profile),
        name="api_get_author_profile"),
    path(
        "author/<uuid:author_id>/posts",
        csrf_exempt(views.specific_author_posts),
        name="api_get_specific_author_posts"),
    path(
        "author/<uuid:author_uuid>/friends",
        csrf_exempt(views.author_friends),
        name="api_get_author_friends"),
    path(
        "author/<uuid:author_uuid>/friends/<path:author_friend_url>",
        csrf_exempt(views.author_friends_with_author),
        name="api_get_author_friends_with_author"),
    path(
        "friendrequest",
        csrf_exempt(views.friend_request),
        name="api_friend_request"),
    path(
        "whoami",
        csrf_exempt(views.who_am_i),
        name="api_who_am_i"),
    path(
        "cansee/<uuid:author_id>/<uuid:post_id>",
        csrf_exempt(views.can_see),
        name="api_can_see"),
    path(
        "author/<uuid:author_id>/github",
        csrf_exempt(views.github_posts),
        name= "api_get_author_github_posts"
    )
]
