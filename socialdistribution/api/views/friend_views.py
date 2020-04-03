from django.http import JsonResponse
from django.core.paginator import Paginator

from ..decorators import check_auth

from urllib import parse
from profiles.models import Author, AuthorFriend
from posts.models import Post, Comment
from profiles.utils import getFriendsOfAuthor
from ..utils import (
    post_to_dict,
    comment_to_dict,
    author_to_dict,
    is_valid_post,
    insert_post,
    update_post,
    is_valid_comment,
    insert_comment,
    validate_friend_request,
    author_can_see_post,
    validate_author_friends_post_query,
)

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
    author_friends = getFriendsOfAuthor(author)

    if request.method == "GET":
        author_friends_urls = [
            author_friend.friend.url for author_friend in author_friends
        ]
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

        author_friends_urls = [
            author_friend.friend.url for author_friend in author_friends
        ]
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
    author_friends = getFriendsOfAuthor(author)

    if request.method == "GET":
        author_friend_url_cleaned = parse.unquote(author_friend_url)
        author_friends_urls = [
            author_friend.friend.url for author_friend in author_friends
        ]
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
        # ensure user is authenticated
        if request.user.is_anonymous:
            response_body = {
                "query": "friendrequest",
                "success": False,
                "message": "Must be authenticated to send a friend request",
            }
            return JsonResponse(response_body, status=403)

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

        author = Author.objects.get(id=request_body["author"]["id"])
        friend = Author.objects.get(id=request_body["friend"]["id"])

        # make sure authenticated user is the one sending the friend request
        if author != request.user:
            response_body = {
                "query": "friendrequest",
                "success": False,
                "message": "Cannot send a friend request for somebody else",
            }
            return JsonResponse(response_body, status=403)

        friend_req = AuthorFriend(author=author, friend=friend)

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
