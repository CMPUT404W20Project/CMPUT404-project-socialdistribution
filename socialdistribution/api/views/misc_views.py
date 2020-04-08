from django.http import JsonResponse

from profiles.models import Author
from posts.models import Post

from ..decorators import check_auth

from ..utils import (
    author_can_see_post,
    author_to_dict,
    is_server_request
)


@check_auth
def who_am_i(request):
    response_body = {"query": "whoami", "success": True}

    if request.user.is_anonymous:
        response_body["author"] = "Server"
    else:
        response_body["author"] = author_to_dict(request.user)

    return JsonResponse(response_body)


@check_auth
def can_see(request, author_id, post_id):

    if is_server_request(request):
        return JsonResponse({"cansee": True})

    author = Author.objects.get(id=author_id)
    post = Post.objects.get(id=post_id)

    if author_can_see_post(author.url, post.serialize()):
        return JsonResponse({"cansee": True})
    else:
        return JsonResponse({"cansee": False})
