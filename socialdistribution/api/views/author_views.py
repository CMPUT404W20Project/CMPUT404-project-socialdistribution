from django.http import JsonResponse
from django.core.paginator import Paginator

from ..decorators import check_auth


from profiles.models import Author
from posts.models import Post
from profiles.utils import get_friend_profiles_of_author
from posts.utils import get_posts
from socialdistribution.utils import get_hostname
from ..utils import (
    post_to_dict,
    author_to_dict,
    author_can_see_post,
    is_server_request,
)


@check_auth
def specific_author_posts(request, author_id):
    # this view only accepts GET, 405 Method Not Allowed for other methods
    if request.method != "GET":
        response_body = {
            "query": "posts",
            "success": False,
            "message": f"Invalid method: {request.method}",
        }
        return JsonResponse(response_body, status=405)

    authors = Author.objects.filter(id=author_id)

    # author does not exist - 404 Not Found
    if authors.count() == 0:
        response_body = {
                "query": "posts",
                "success": False,
                "message": "That author does not exist",
            }
        return JsonResponse(response_body, status=404)

    author = authors[0]
    author_posts = Post.objects.filter(author=author)

    # get only visible posts
    visible_post_ids = []
    for post in author_posts:
        if is_server_request(request) or author_can_see_post(request.user.url, post_to_dict(post)):
            visible_post_ids.append(post.id)

    visible_author_posts = author_posts.filter(id__in=visible_post_ids).order_by('-published')

    # page number query parameter
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 0
    else:
        page_number = int(page_number)

    # page size query parameter
    page_size = request.GET.get("size")
    if page_size is None:
        page_size = 50
    else:
        page_size = int(page_size)

    # bad page size
    if page_size <= 0:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "Page size must be a positive integer",
        }
        return JsonResponse(response_body, status=400)

    # paginates our QuerySet
    paginator = Paginator(visible_author_posts, page_size)

    # bad page number
    if page_number < 0 or page_number >= paginator.num_pages:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "That page does not exist",
        }
        return JsonResponse(response_body, status=404)

    # get the page
    # note: the off-by-ones here are because Paginator is 1-indexed
    # and the example article responses are 0-indexed
    page_obj = paginator.page(str(int(page_number) + 1))

    # response body - to be converted into JSON and returned in response
    response_body = {
        "query": "posts",
        "count": paginator.count,
        "size": int(page_size),
        "posts": [post_to_dict(post) for post in page_obj],
    }

    # give a url to the next page if it exists
    if page_obj.has_next():
        next_uri = f"/api/author/{author.id}/posts?page={page_obj.next_page_number() - 1}&size={page_size}"
        response_body["next"] = request.build_absolute_uri(next_uri)

    # give a url to the previous page if it exists
    if page_obj.has_previous():
        previous_uri = f"/api/author/{author.id}/posts?page={page_obj.previous_page_number() - 1}&size={page_size}"
        response_body["previous"] = request.build_absolute_uri(previous_uri)

    return JsonResponse(response_body)


@check_auth
def author_posts(request):
    # this view only accepts GET, 405 Method Not Allowed for other methods
    if request.method != "GET":
        response_body = {
            "query": "posts",
            "success": False,
            "message": f"Invalid method: {request.method}",
        }
        return JsonResponse(response_body, status=405)

    all_local_remote_posts = get_posts()

    # get only visible posts
    filtered_posts = []
    for post in all_local_remote_posts:
        if is_server_request(request) or author_can_see_post(request.user.url, post):
            hostname = get_hostname()
            if hostname[-1] != "/":
                hostname += "/"
            post["source"] = hostname + "/api/author/posts"
            filtered_posts.append(post)

    # page number query parameter
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 0
    else:
        page_number = int(page_number)

    # page size query parameter
    page_size = request.GET.get("size")
    if page_size is None:
        page_size = 50
    else:
        page_size = int(page_size)

    # bad page size
    if page_size <= 0:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "Page size must be a positive integer",
        }
        return JsonResponse(response_body, status=400)

    # paginates our QuerySet
    paginator = Paginator(filtered_posts, page_size)

    # bad page number
    if page_number < 0 or page_number >= paginator.num_pages:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "That page does not exist",
        }
        return JsonResponse(response_body, status=404)

    # get the page
    # note: the off-by-ones here are because Paginator is 1-indexed
    # and the example article responses are 0-indexed
    page_obj = paginator.page(str(int(page_number) + 1))

    # response body - to be converted into JSON and returned in response
    response_body = {
        "query": "posts",
        "count": paginator.count,
        "size": int(page_size),
        "posts": [post for post in page_obj],
    }

    # give a url to the next page if it exists
    if page_obj.has_next():
        next_uri = f"/api/author/posts?page={page_obj.next_page_number() - 1}&size={page_size}"
        response_body["next"] = request.build_absolute_uri(next_uri)

    # give a url to the previous page if it exists
    if page_obj.has_previous():
        previous_uri = f"/api/author/posts?page={page_obj.previous_page_number() - 1}&size={page_size}"
        response_body["previous"] = request.build_absolute_uri(previous_uri)

    return JsonResponse(response_body)


@check_auth
def author_profile(request, author_id):
    if request.method == "GET":
        authors = Author.objects.filter(id=author_id)

        # author does not exist - 404 Not Found
        if authors.count() == 0:
            response_body = {
                "query": "authorProfile",
                "success": False,
                "message": "That author does not exist",
            }
            return JsonResponse(response_body, status=404)

        author = authors[0]

        response_body = author_to_dict(author)

        # Might cause issues since these could be remote authors
        response_body["friends"] = get_friend_profiles_of_author(author.url)

        return JsonResponse(response_body)

    response_body = {
        "query": "authorProfile",
        "success": False,
        "message": f"Invalid method: {request.method}",
    }
    return JsonResponse(response_body, status=405)
