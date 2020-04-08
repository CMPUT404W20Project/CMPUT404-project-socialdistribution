from django.http import JsonResponse
from django.core.paginator import Paginator

from ..decorators import check_auth

from profiles.models import Author
from posts.models import Post, Comment
from ..utils import (
    post_to_dict,
    comment_to_dict,
    is_valid_post,
    insert_post,
    update_post,
    is_valid_comment,
    insert_comment,
    author_can_see_post,
    is_server_request
)

import json


@check_auth
def posts(request):
    # get public posts
    if request.method == "GET":
        # get a list of all "PUBLIC" visibility posts on our node
        public_posts = Post.objects.filter(visibility="PUBLIC").order_by('-published')

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
        paginator = Paginator(public_posts, page_size)

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
            "posts": [post_to_dict(post, request) for post in page_obj],
        }

        # give a url to the next page if it exists
        if page_obj.has_next():
            next_uri = f"/api/posts?page={page_obj.next_page_number() - 1}&size={page_size}"
            response_body["next"] = request.build_absolute_uri(next_uri)

        # give a url to the previous page if it exists
        if page_obj.has_previous():
            previous_uri = f"/api/posts?page={page_obj.previous_page_number() - 1}&size={page_size}"
            response_body["previous"] = request.build_absolute_uri(previous_uri)

        return JsonResponse(response_body)

    # insert new post
    elif request.method == "POST":
        request_body = json.loads(request.body)

        # post is not valid - 400 Bad Request or 422 Unprocessable Entity
        if not is_valid_post(request_body):
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Invalid post",
            }
            return JsonResponse(response_body, status=400)

        author = Author.objects.get(id=request_body["author"]["id"])
        # wrong author
        if author != request.user:
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Must login to post",
            }
            return JsonResponse(response_body, status=403)

        if "id" in request_body.keys():
            posts = Post.objects.filter(id=request_body["id"])
            # post already exists
            if posts.count() > 0:
                response_body = {
                    "query": "posts",
                    "success": False,
                    "message": "Post already exists",
                }
                return JsonResponse(response_body, status=400)

        # valid post --> insert to DB
        post = insert_post(request_body)

        return JsonResponse(post_to_dict(post, request))

    # insert new post
    # note: PUT requires an ID whereas POST does not
    elif request.method == "PUT":
        request_body = json.loads(request.body)

        # post is not valid - 400 Bad Request or 422 Unprocessable Entity
        if not is_valid_post(request_body):
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Invalid post",
            }
            return JsonResponse(response_body, status=400)

        author = Author.objects.get(id=request_body["author"]["id"])
        # wrong author
        if author != request.user:
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Must login to post",
            }
            return JsonResponse(response_body, status=403)

        if "id" in request_body.keys():
            posts = Post.objects.filter(id=request_body["id"])
            # post already exists
            if posts.count() > 0:
                response_body = {
                    "query": "posts",
                    "success": False,
                    "message": "Post already exists",
                }
                return JsonResponse(response_body, status=400)
        else:
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Missing post id",
            }
            return JsonResponse(response_body, status=400)

        # valid post --> insert to DB
        post = insert_post(request_body)

        return JsonResponse(post_to_dict(post, request))

    # invalid method
    response_body = {
        "query": "posts",
        "success": False,
        "message": f"Invalid method: {request.method}",
    }
    return JsonResponse(response_body, status=405)


@check_auth
def single_post(request, post_id):
    posts = Post.objects.filter(id=post_id)

    if posts.count() > 0:
        if (not is_server_request(request) and
                not author_can_see_post(request.user.url, posts[0].serialize())):
            response_body = {
                "query": "posts",
                "success": False,
                "message": "You don't have permission to access that post",
            }
            return JsonResponse(response_body, status=403)

    # GET a post which doesn't exist - 404 Not Found
    if request.method == "GET" and posts.count() == 0:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "Post does not exist",
        }
        return JsonResponse(response_body, status=404)

    # POST (insert) a post which already exists - 403 Forbidden
    if request.method == "POST" and posts.count() > 0:
        response_body = {
            "query": "posts",
            "success": False,
            "message": "Post already exists",
        }
        return JsonResponse(response_body, status=400)

    # GET a post which exists - return post in JSON format
    if request.method == "GET" and posts.count() > 0:
        response_body = {
            "query": "posts",
            "post": post_to_dict(posts[0], request)
        }

        return JsonResponse(response_body)

    # PUT a post which exists - update post
    if request.method == "PUT" and posts.count() > 0:
        post_to_update = posts[0]

        if post_to_update.author != request.user:
            response_body = {
                "query": "posts",
                "success": False,
                "message": "You don't have permission to access that post",
            }
            return JsonResponse(response_body, status=403)

        request_body = json.loads(request.body)

        # post is not valid - 400 Bad Request or 422 Unprocessable Entity
        if not is_valid_post(request_body):
            response_body = {
                "query": "posts",
                "success": False,
                "message": "Invalid post",
            }
            return JsonResponse(response_body, status=400)

        # valid post --> update existing post
        post = update_post(post_to_update, request_body)

        return JsonResponse(post_to_dict(post, request))

    # delete a post
    if request.method == "DELETE" and posts.count() > 0:
        post = posts[0]

        if post.author != request.user:
            response_body = {
                "query": "posts",
                "success": False,
                "message": "You don't have permission to access that post",
            }
            return JsonResponse(response_body, status=403)

        post.delete()

        response_body = {
            "query": "posts",
            "success": True,
            "message": "Post deleted",
        }
        return JsonResponse(response_body)

    if request.method not in ["GET", "PUT", "DELETE", "POST"]:
        # invalid method
        response_body = {
            "query": "posts",
            "success": False,
            "message": f"Invalid method: {request.method}",
        }
        return JsonResponse(response_body, status=405)


@check_auth
def post_comments(request, post_id):
    # get the post
    posts = Post.objects.filter(id=post_id)

    # post does not exist - 404 Not Found
    if posts.count() == 0:
        response_body = {
            "query": "comments",
            "success": False,
            "message": "Post does not exist",
        }
        return JsonResponse(response_body, status=404)

    post = posts[0]

    if not is_server_request(request) and not author_can_see_post(request.user.url, post.serialize()):
        response_body = {
            "query": "comments",
            "success": False,
            "message": "You don't have permission to see that post",
        }
        return JsonResponse(response_body, status=403)

    # get comments for the post
    if request.method == "GET":
        # get the comments for the post
        comments = Comment.objects.filter(post=post).order_by('-published')

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
                "query": "comments",
                "success": False,
                "message": "Page size must be a positive integer",
            }
            return JsonResponse(response_body, status=400)

        # paginates our QuerySet
        paginator = Paginator(comments, page_size)

        # bad page number
        if page_number < 0 or page_number >= paginator.num_pages:
            response_body = {
                "query": "comments",
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
            "query": "comments",
            "count": paginator.count,
            "size": int(page_size),
            "comments": [comment_to_dict(comment) for comment in page_obj],
        }

        # give a url to the next page if it exists
        if page_obj.has_next():
            next_uri = f"/api/posts/{post.id}/comments?page={page_obj.next_page_number() - 1}&size={page_size}"
            response_body["next"] = request.build_absolute_uri(next_uri)

        # give a url to the previous page if it exists
        if page_obj.has_previous():
            previous_uri = f"/api/posts/{post.id}/comments?page={page_obj.previous_page_number() - 1}&size={page_size}"
            response_body["previous"] = request.build_absolute_uri(previous_uri)

        return JsonResponse(response_body)


    # post a comment
    elif request.method == "POST":

        request_body = json.loads(request.body)

        # comment is not valid - 400 Bad Request or 422 Unprocessable Entity
        if not is_valid_comment(request_body):
            response_body = {
                "query": "addComment",
                "success": False,
                "message": "Invalid comment",
            }

            return JsonResponse(response_body, status=400)

        author_url = request_body["comment"]["author"]["id"]

        if not is_server_request(request) and author_url != request.user.url:
            response_body = {
                "query": "addComment",
                "success": False,
                "message": "Cannot post comment from somebody else's account",
            }
            return JsonResponse(response_body, status=403)

        # valid post --> insert to DB
        comment = insert_comment(post, request_body)

        response_body = {
            "query": "addComment",
            "success": True,
            "message": "Comment added",
        }
        return JsonResponse(response_body)

    response_body = {
        "query": "comments",
        "success": False,
        "message": f"Invalid method: {request.method}",
    }
    return JsonResponse(response_body, status=405)
