from django.http import JsonResponse

from ..decorators import check_auth

from urllib import parse
from profiles.models import Author, AuthorFriend
from profiles.utils import get_friend_urls_of_author
from ..utils import (
    validate_friend_request,
    validate_author_friends_post_query,
    is_server_request
)

from socialdistribution.utils import get_url_part
import json


@check_auth
def author_friends(request, author_uuid):

    # this view only accepts GET, and POSTS,
    # 405 Method Not Allowed for other methods
    if request.method != "GET" and request.method != "POST":
        response_body = {
            "query": "friends",
            "success": False,
            "message": f"Invalid method: {request.method}",
        }
        return JsonResponse(response_body, status=405)

    author = Author.objects.filter(id=author_uuid)
    # author does not exist - 404 Not Found
    if author.count() == 0:
        response_body = {
                "query": "friends",
                "success": False,
                "message": "That author does not exist",
            }
        return JsonResponse(response_body, status=404)

    author = author[0]

    if request.method == "GET":
        author_friends_urls = get_friend_urls_of_author(author.url)
        response_body = {
            "query": "friends",
            "authors": author_friends_urls,
        }
        return JsonResponse(response_body)

    elif request.method == "POST":
        request_body = json.loads(request.body)
        status = validate_author_friends_post_query(request_body)
        # invalid request
        if status != 200:
            response_body = {
                "query": "friends",
                "success": False,
                "message": "Invalid request",
            }
            return JsonResponse(response_body, status=status)

        # full URL of author, not just id
        request_body_author = request_body['author']
        if author.url != request_body_author:
            response_body = {
                "query": "friends",
                "success": False,
                "message": "Bad request",
            }
            return JsonResponse(response_body, status=400)

        author_friends_urls = get_friend_urls_of_author(author.url)

        request_body_authors = request_body['authors']

        response_body = {
            "query": "friends",
            "author": author.url,
            "authors": [
                author_url
                for author_url in request_body_authors
                if author_url in author_friends_urls
            ]
        }

        return JsonResponse(response_body)

    response_body = {
        "query": "friends",
        "success": False,
        "message": "Internal server error",
    }

    return JsonResponse(response_body, status=500)


@check_auth
def author_friends_with_author(request, author_uuid, author_friend_url):
    # this view only accepts GET,
    # 405 Method Not Allowed for other methods
    if request.method != "GET":
        response_body = {
            "query": "friends",
            "success": False,
            "message": f"Invalid method: {request.method}",
        }
        return JsonResponse(response_body, status=405)

    author = Author.objects.filter(id=author_uuid)
    # author does not exist - 404 Not Found
    if author.count() == 0:
        response_body = {
                "query": "friends",
                "success": False,
                "message": "That author does not exist",
            }
        return JsonResponse(response_body, status=404)

    author = author[0]

    if request.method == "GET":
        author_friend_url_cleaned = parse.unquote(author_friend_url)
        author_friends_urls = get_friend_urls_of_author(author.url)
        friends = False
        for url in author_friends_urls:
            if author_friend_url_cleaned in url:
                friends = True
                break
        response_body = {
            "query": "friends",
            "authors": [author.url, author_friend_url_cleaned],
            "friends": friends,
        }

        return JsonResponse(response_body)

    response_body = {
        "query": "friends",
        "success": False,
        "message": "Internal server error",
    }

    return JsonResponse(response_body, status=500)


@check_auth
def friend_request(request):
    if request.method == "POST":

        request_body = json.loads(request.body)

        # check that the friend request is valid
        status = validate_friend_request(request_body)

        # invalid request
        if status != 200:
            response_body = {
                "query": "friendrequest",
                "success": False,
                "message": "Invalid request",
            }
            return JsonResponse(response_body, status=status)

        # In this case, the id is the URL
        sender_url = request_body["author"]["id"]
        receiver_url = request_body["friend"]["id"]

        receiver_id = get_url_part(receiver_url, -1)

        if not Author.objects.filter(id=receiver_id).count():
            # ensure receiving author exists on server
            response_body = {
                "query": "friendrequest",
                "success": False,
                "message": "Author does not exist",
            }
            return JsonResponse(response_body, status=404)

        # Only the author logged in can make a request for
        # themselves, and no one else

        if not is_server_request(request) and request.user.url != sender_url:
            response_body = {
                "query": "friendrequest",
                "success": False,
                "message": "Cannot make a request for another author",
            }
            return JsonResponse(response_body, status=403)

        # Need to add check that we can only add friends if
        # we have server credentials of remote authors

        friend_req = AuthorFriend(author=sender_url, friend=receiver_url)

        friend_req.save()

        response_body = {
            "query": "friendrequest",
            "success": True,
            "message": "Friend request sent",
        }
        return JsonResponse(response_body)

    response_body = {
        "query": "friendrequest",
        "success": False,
        "message": f"Invalid method: {request.method}",
    }
    return JsonResponse(response_body, status=405)
