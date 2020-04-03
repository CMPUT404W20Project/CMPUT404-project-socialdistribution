from django.http import JsonResponse

from profiles.models import Author
from posts.models import Post

from ..decorators import check_auth

from ..utils import (
    author_can_see_post,
    author_to_dict,
)


@check_auth
def who_am_i(request):
    response_body = {"query": "whoami", "success": True}

    if request.user.is_anonymous:
        response_body["author"] = "Anonymous user (unauthenticated)"
    else:
        response_body["author"] = author_to_dict(request.user)

    return JsonResponse(response_body)


@check_auth
def can_see(request, author_id, post_id):
    author = Author.objects.get(id=author_id)
    post = Post.objects.get(id=post_id)

    if author_can_see_post(author, post):
        return JsonResponse({"cansee": True})
    else:
        return JsonResponse({"cansee": False})
