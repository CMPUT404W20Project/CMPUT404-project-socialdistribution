from django.http import JsonResponse

from profiles.models import Author
from posts.models import Post

from ..decorators import check_auth

from ..utils import (
    author_can_see_post,
    author_to_dict,
    is_server_request,
    post_to_dict
)
import requests


@check_auth
def who_am_i(request):
    response_body = {"query": "whoami", "success": True}

    if is_server_request(request):
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

    if author_can_see_post(author.url, post_to_dict(post)):
        return JsonResponse({"cansee": True})
    else:
        return JsonResponse({"cansee": False})


@check_auth
def github_posts(request):
    if request.method == "GET":
        author = request.user

        # get the github activities of the author
        github_name = author.github
        # if user doesn't have a github account, return 404
        if github_name == '':
            response_body = {
                "query": "github_posts",
                "success": False,
                "message": "The author isn't linked to a github account",
            }
            return JsonResponse(response_body, status=404)

        github_name = author.github.split("/")[3]
        github_name = github_name.lower()
        github_url = 'https://api.github.com/users/' + github_name + '/events'
        r = requests.get(url=github_url)

        # if the github api doesn't return 200,
        # then return whatever the github api endpoint returns
        if r.status_code != 200:
            response_body = {
                "query": "github_posts",
                "success": False,
                "message": "Can't retrieve the author's github activities",
            }
            return JsonResponse(response_body, status=r.status_code)

        github_activities = r.json()
        for activity in github_activities:

            git_id = activity['id']
            existing_post = Post.objects.filter(author=author, description=git_id).exists()

            if not existing_post:
                title = activity['type']
                published = activity['created_at']
                type = activity['type']
                repo_name = activity['repo']['name']
                payload = activity['payload']

                content = "["+ repo_name +"](https://github.com/"+ repo_name + ") \r\n "
                if type == 'PullRequestEvent':
                    content += payload['pull_request']['body']
                elif type == 'PushEvent':
                    for i in range(len(payload['commits'])):
                        content += "["+ payload['commits'][i]['message'].replace('\n\n', ' ') +"]("+ payload['commits'][i]['url'] + ") \r\n "
                elif type == 'PullRequestReviewCommentEvent':
                    content += payload['comment']['body']
                elif type == 'IssueCommentEvent':
                    content += "[Detail]("+ payload['comment']['html_url'] + ")"
                elif type == 'IssuesEvent':
                    content += "["+ payload['issue']['title'] +"]("+ payload['issue']['html_url'] + ")"

                github_post = Post(author=author, title=title, description=git_id, content=content, published=published, contentType='text/markdown')
                github_post.save()

        response_body = {
            "query": "github_posts",
            "success": True,
            "message": "Github activities loaded",
        }
        return JsonResponse(response_body)

    response_body = {
        "query": "github_posts",
        "success": False,
        "message": f"Invalid method: {request.method}",
    }

    return JsonResponse(response_body, status=405)
