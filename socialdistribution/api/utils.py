from django.utils.timezone import make_aware
from django.core.paginator import Paginator

from profiles.models import Author, AuthorFriend
from posts.models import Post, Comment
from profiles.utils import get_friend_urls_of_author
from servers.models import Server
from socialdistribution.utils import get_host, get_hostname

from datetime import datetime
import dateutil.parser


def is_server_request(request):
    return request.user.is_anonymous


def authenticate_server(username, password):
    try:
        if Server.objects.get(local_server_user=username,
                              local_server_pass=password):
            return True
        return False
    except Server.DoesNotExist:
        return False


def post_to_dict(post):
    comments = Comment.objects.filter(post=post).order_by("-published")

    page_size = 50

    # paginates our QuerySet
    paginator = Paginator(comments, page_size)

    # get the page
    # note: the off-by-ones here are because Paginator is 1-indexed
    # and the example article responses are 0-indexed
    page_obj = paginator.page("1")

    post_dict = {
        "title": post.title,
        "source": post.source,
        "origin": post.origin,
        "description": post.description,
        "contentType": post.contentType,
        "content": post.content,
        "author": author_to_dict(post.author),
        "categories": ["web", "tutorial"],
        "count": paginator.count,
        "size": page_size,
        "comments": [comment_to_dict(comment) for comment in comments],
        "published": post.published.isoformat(),
        "id": post.id,
        "visibility": post.visibility,
        "visibleTo": post.visibleTo,
        "unlisted": post.unlisted,
    }

    # give a url to the next page if it exists
    if page_obj.has_next():
        next_uri = f"/api/posts/{post.id}/comments?page={page_obj.next_page_number() - 1}"
        hostname = get_hostname()
        if hostname[-1] == "/":
            hostname = hostname[:-1]

        post_dict["next"] = hostname + next_uri

    return post_dict


def author_to_dict(author):
    return author.serialize()


def comment_to_dict(comment):
    return comment.serialize()


def is_valid_post(post_dict):
    fields = [
        # field, type, required
        ("title", str, True),
        ("description", str, True),
        ("contentType", str, True),
        ("content", str, True),
        ("categories", list, True),
        ("visibility", str, True),
        ("unlisted", bool, True),
        ("author", dict, True),
        ("published", str, False),
    ]

    post_fields = post_dict.keys()

    # general validation
    for field, field_type, required in fields:
        # missing a required field
        if required and field not in post_fields:
            return False
        if field in post_fields:
            # wrong type for field
            if not isinstance(post_dict[field], field_type):
                return False

    # make sure if they included a timestamp, it's a valid timestamp
    if "published" in post_fields:
        try:
            datetime = dateutil.parser.isoparse(post_dict["published"])
        except:
            return False

    # make sure author exists
    authors = Author.objects.filter(id=post_dict["author"]["id"])
    if authors.count() == 0:
        return False

    return True


def insert_post(post_dict):
    author = Author.objects.get(id=post_dict["author"]["id"])

    post_fields = post_dict.keys()

    if "published" in post_fields:
        post_datetime = make_aware(
            dateutil.parser.isoparse(post_dict["published"]))
    else:
        post_datetime = datetime.utcnow()

    if "id" in post_fields:
        post = Post(
            id=post_dict["id"],
            title=post_dict["title"],
            description=post_dict["description"],
            categories=post_dict["categories"],
            published=post_datetime,
            author=author,
            visibility=post_dict["visibility"],
            unlisted=post_dict["unlisted"],
            contentType=post_dict["contentType"],
        )
    else:
        post = Post(
            title=post_dict["title"],
            description=post_dict["description"],
            categories=post_dict["categories"],
            published=post_datetime,
            author=author,
            visibility=post_dict["visibility"],
            unlisted=post_dict["unlisted"],
            contentType=post_dict["contentType"],
        )

    post.save()

    return post


def update_post(post, new_post_dict):
    new_fields = new_post_dict.keys()

    if "title" in new_fields:
        post.title = new_post_dict["title"]
    if "description" in new_fields:
        post.description = new_post_dict["description"]
    if "categories" in new_fields:
        post.categories = new_post_dict["categories"]
    if "published" in new_fields:
        post_datetime = make_aware(
            dateutil.parser.isoparse(new_post_dict["published"]))
        post.published = post_datetime
    if "visibility" in new_fields:
        post.visibility = new_post_dict["visibility"]
    if "unlisted" in new_fields:
        post.unlisted = new_post_dict["unlisted"]
    if "contentType" in new_fields:
        post.contentType = new_post_dict["contentType"]

    post.save()

    return post


def is_valid_comment(comment_dict):
    comment_dict_fields = comment_dict.keys()

    # validate base fields
    for field, field_type in [("query", str), ("post", str), ("comment", dict)]:
        if field not in comment_dict.keys() or not isinstance(
            comment_dict[field], field_type
        ):
            return False

    # validate comment fields
    for field, field_type in [("author", dict), ("comment", str), ("contentType", str), ("id", str)]:
        if field not in comment_dict["comment"].keys() or not isinstance(
            comment_dict["comment"][field], field_type
        ):
            return False

    # make sure "published" is a valid ISO-8601 timestamp
    if "published" in comment_dict["comment"].keys():
        try:
            datetime = dateutil.parser.isoparse(
                comment_dict["comment"]["published"])
        except:
            return False

    # make sure that the comment doesn't already exist
    comments = Comment.objects.filter(id=comment_dict["comment"]["id"])
    if comments.count() > 0:
        return False

    return True


def insert_comment(post, comment_dict):
    # get the author specified by the comment
    author_url = comment_dict["comment"]["author"]["id"]

    if "published" in comment_dict["comment"].keys():
        comment_datetime = make_aware(
            dateutil.parser.isoparse(comment_dict["comment"]["published"])
        )
    else:
        comment_datetime = datetime.utcnow()

    comment = Comment(
        id=comment_dict["comment"]["id"],
        comment=comment_dict["comment"]["comment"],
        published=comment_datetime,
        post=post,
        author=author_url,
        contentType=comment_dict["comment"]["contentType"]
    )

    comment.save()

    return comment


def validate_author_friends_post_query(request_dict):
    fields_required = [
        # field, type, required
        ("query", str),
        ("author", str),
        ("authors", list),
    ]
    for field, field_type in fields_required:
        # Bad Request
        if field not in request_dict.keys() or not isinstance(
            request_dict[field], field_type
        ):
            return 400

    return 200


def validate_friend_request(request_dict):
    for field, field_type in [("query", str), ("author", dict), ("friend", dict)]:
        # Bad Request
        if field not in request_dict.keys() or not isinstance(
            request_dict[field], field_type
        ):
            return 400

    for author in [request_dict["author"], request_dict["friend"]]:
        # check fields
        for field, field_type in [
            ("id", str),
            ("host", str),
            ("displayName", str),
            ("url", str),
        ]:
            # Bad Request
            if field not in author.keys() or not isinstance(author[field], field_type):
                return 400

        # make sure author exists
        results = Author.objects.filter(id=author["id"])
        if results.count() == 0:
            # Not Found
            return 404

    author = Author.objects.get(id=request_dict["author"]["id"])
    friend = Author.objects.get(id=request_dict["friend"]["id"])

    # make sure author and friend aren't the same user
    if author.id == friend.id:
        # Bad Request
        return 400

    # make sure friend request doesn't exist already
    results = AuthorFriend.objects.filter(author=author, friend=friend)
    if results.count() > 0:
        # Bad Request
        return 400

    # OK
    return 200


def author_can_see_post(author_url, post_dict):

    post_author_url = post_dict["author"]["id"]

    if not author_url or not post_author_url:
        print("No url provided")
        return False

    if author_url == post_author_url:
        return True

    if (post_dict["visibility"] == "PUBLIC"):
        return True

    if (post_dict["visibility"] == "PRIVATE"):
        if author_url == post_author_url:
            return True
        elif author_url in post_dict["visibleTo"]:
            return True

    # TODO: check this
    if (post_dict["visibility"] == "SERVERONLY" and
       get_host(author_url) in post_dict["author"]["host"]):
        return True

    if post_dict["visibility"] == "FRIENDS":
        post_author_friends = get_friend_urls_of_author(post_author_url)
        if author_url in post_author_friends:
            return True

    if post_dict["visibility"] == "FOAF":
        post_author_friends = get_friend_urls_of_author(post_author_url)

        if author_url in post_author_friends:
            return True

        author_friends = get_friend_urls_of_author(author_url)

        author_friend_ids = set(author_friends)
        post_author_friend_ids = set(post_author_friends)

        if len(author_friend_ids & post_author_friend_ids) > 0:
            return True

    return False
