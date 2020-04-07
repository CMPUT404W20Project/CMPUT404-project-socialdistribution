from profiles.models import Author, AuthorFriend
from servers.utils import api_request_to_server
from socialdistribution.utils import (validate_instance,
                                      get_host, get_url_part,
                                      get_hostname,)
from urllib import parse

AUTHOR_ENDPOINT = "author/"
AUTHOR_PROFILE_ENDPOINT = AUTHOR_ENDPOINT + "/%s"
AUTHOR_FIELDS = ["id", "host", "displayName", "url"]
AUTHOR_PROFILE_FIELDS = AUTHOR_FIELDS.append("friends")

AUTHOR_FRIENDS_ENDPOINT = AUTHOR_ENDPOINT + "%s/friends/"
AUTHOR_FRIENDS_FIELDS = ["authors"]
CHECK_FRIEND_ENDPOINT = AUTHOR_ENDPOINT + "%s/friends/%s"
CHECK_FRIEND_FIELDS = AUTHOR_FRIENDS_FIELDS.append("friends")


def is_local_author(author_url):
    if get_hostname() in author_url:
        return True
    return False


def get_local_profile(author_url):
    author_id = get_url_part(author_url, -1)
    try:
        author = Author.objects.get(id=author_id).serialize()
        author["friends"] = get_friend_urls_of_author(author_url)
        return author
    except Author.DoesNotExist:
        print("Local author does not exist!")
        return None


def validate_remote_author_profile_response(profile):
    if not validate_instance(profile, AUTHOR_PROFILE_FIELDS, "author_profile"):
        return False

    for friend in profile.get("friend"):
        if not validate_instance(friend, AUTHOR_FIELDS, "author"):
            return False

    return True


def get_remote_profile(author_url):
    author_host = get_host(author_url)
    author_id = get_url_part(author_url, -1)
    author_profile_endpoint = AUTHOR_PROFILE_ENDPOINT % (author_id)
    profile = api_request_to_server(author_host, author_profile_endpoint)

    if not profile:
        print("Unable to get remote profile %s from %s" % (author_id,
                                                           author_host))
        return None

    if not validate_remote_author_profile_response(profile):
        print("Received a malformed response from %s/%s."
              % (author_host, author_profile_endpoint))
        return None

    return profile


def get_profile(author_url):
    if is_local_author(author_url):
        return get_local_profile(author_url)
    return get_remote_profile(author_url)


def get_author_friend_relationships(author_url):
    all_author_friend_entries = AuthorFriend.objects.all()
    # Find all people that the author follows
    author_friends = all_author_friend_entries.filter(author=author_url)
    # Find all people that follow author
    friends_author = all_author_friend_entries.filter(friend=author_url)

    return author_friends, friends_author


def follows_local(author_url, followee_url):
    if AuthorFriend.objects.filter(author=author_url, friend=followee_url):
        return True
    return False


def validate_remote_author_friends_response(friends):
    if not validate_instance(friends, AUTHOR_FRIENDS_FIELDS,
                             "remote_author_friends"):
        return False
    return True


def validate_follows_remote_response(is_friend):
    if not validate_instance(is_friend, CHECK_FRIEND_FIELDS,
                             "follows_remote"):
        return False
    return True


def follows_remote(author_url, followee_url):
    author_host = get_host(author_url)
    author_id = get_url_part(author_url, -1)
    followee_url_cleaned = parse.quote(followee_url, safe='~()*!.\'')
    author_is_friend_endpoint = CHECK_FRIEND_ENDPOINT % (author_id,
                                                         followee_url_cleaned)
    is_friend = api_request_to_server(author_host, author_is_friend_endpoint)

    if not is_friend:
        print("Unable to get follows_remote author %s on %s" % (author_id,
                                                                author_host))
        return None

    if not validate_follows_remote_response(is_friend):
        print("Received a malformed response from %s/%s."
              % (author_host, author_is_friend_endpoint))
        return None

    if str(is_friend.get("friends")).lower() == "false":
        return False
    return True


# object: local - local; remote - local; local - remote
# does author follow
def follows(author_url, followee_url):
    if get_hostname() in author_url:
        return follows_local(author_url, followee_url)
    return follows_remote(author_url, followee_url)


def get_friend_urls_of_author_local(author_url):
    friends = []
    author_follows = AuthorFriend.objects.filter(author=author_url)
    for object in author_follows:
        if follows(object.friend, object.author):
            friends.append(object.friend)
    return friends


def get_friend_urls_of_author_remote(author_url):
    author_host = get_host(author_url)
    author_id = get_url_part(author_url, -1)
    author_friends_endpoint = AUTHOR_FRIENDS_ENDPOINT % (author_id)
    friends = api_request_to_server(author_host, author_friends_endpoint)

    if not friends:
        print("Unable to get follows_remote author %s on %s" % (author_id,
                                                                author_host))
        return None

    if not validate_remote_author_friends_response(friends):
        print("Received a malformed response from %s/%s."
              % (author_host, author_friends_endpoint))
        return None

    return friends.get("authors")


def get_friend_urls_of_author(author_url):

    if is_local_author(author_url):
        return get_friend_urls_of_author_local(author_url)
    return get_friend_urls_of_author_remote(author_url)


def get_friend_profiles_of_author(author_url):
    friends = []
    friend_urls_of_author = get_friend_urls_of_author(author_url)

    for friend_url in friend_urls_of_author:
        friend_profile = get_profile(friend_url)
        friends.append(friend_profile)
    return friends


def get_friend_requests_to_author(author_url):
    friend_requests_to_author = []
    follows_author = AuthorFriend.objects.filter(friend=author_url)

    # Friend request if person follows author but author does not follow back
    for object in follows_author:
        # If author does not follow them back then it is a friend request
        if not follows(object.friend, object.author):
            friend_requests_to_author.append(object.author)
    return friend_requests_to_author


def get_friend_requests_from_author(author_url):
    friend_requests_from_author = []
    author_follows = AuthorFriend.objects.filter(author=author_url)

    # Friend request sent if author follows person but person does not
    # follow back
    for object in author_follows:
        # If person does not follow author then it is a friend request
        if not follows(object.friend, object.author):
            friend_requests_from_author.append(object)
    return friend_requests_from_author


def isFriend(author_one, author_two):
    if follows(author_one, author_two) and follows(author_two, author_one):
        return True
    return False
