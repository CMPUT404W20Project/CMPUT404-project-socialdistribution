from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from posts.forms import PostForm
from .forms import ProfileForm, ProfileSignup

from .decorators import check_authentication
from .utils import get_friend_profiles_of_author, get_friend_requests_to_author,\
                   get_friend_requests_from_author

from .models import AuthorFriend, Author
import base64


@login_required
def index(request):

    # This a view that display the navigation of the author.
    # In the navigation, author can view/edit it's profile and dashboard.
    # Author can choose their actions such as look at the friends page,
    # post a new post, etc.
    # TODO: remove hardcode
    author = request.user
    template = 'profiles/index_base.html'
    context = {
        'author': author,
    }

    return render(request, template, context)


@csrf_exempt
@login_required
def new_post(request):
    author = request.user
    template = 'vue/new_post.html'
    form = PostForm(request.POST or None, request.FILES or None, initial={'author': author})
    friendList = get_friend_profiles_of_author(author.url)

    context = {
        'form': form,
        'author': author,
        'friendList': friendList
    }

    if request.method == 'POST':
        if form.is_valid():
            new_content = form.save(commit=False)
            cont_type = form.cleaned_data['contentType']
            if(cont_type == "image/png;base64" or cont_type == "image/jpeg;base64"):
                img = form.cleaned_data['image_file']
                new_content.content = (base64.b64encode(img.file.read())).decode("utf-8")
            new_content.save()
            url = reverse('index')
            return HttpResponseRedirect(url)

    return render(request, template, context)

    # author = request.user
    # template = 'posts/posts_form.html'
    # form = PostForm(request.POST or None, request.FILES or None, initial={'author': author})
    # friendList = getFriendsOfAuthor(author)

    # context = {
    #     'form': form,
    #     'author': author,
    #     'friendList': friendList,
    # }

    # if request.method == 'POST':
    #     if form.is_valid():
    #         new_content = form.save(commit=False)
    #         cont_type = form.cleaned_data['contentType']
    #         if(cont_type == "image/png;base64" or cont_type == "image/jpeg;base64"):
    #             img = form.cleaned_data['image_file']
    #             new_content.content = (base64.b64encode(img.file.read())).decode("utf-8")
    #         new_content.save()
    #         url = reverse('index')
    #         return HttpResponseRedirect(url)

    # return render(request, template, context)


def current_visible_posts(request):
    return HttpResponse("Only these posts are visible to you: ")


def author_posts(request, author_id):
    return HttpResponse("Here are the posts of %s: ", author_id)


@login_required
def view_profile(request):
    author = request.user

    return view_author_profile(request, author.id)

    # author = request.user
    # template = 'profiles/profiles_view.html'
    # # form = ProfileForm(instance=author)
    # context = {
    #     'author': author
    # }

    # return render(request, template, context)


@login_required
def edit_profile(request):

    author = request.user
    template = 'profiles/profiles_edit.html'
    form = ProfileForm(request.POST or None, request.FILES or None,
                       instance=author)
    context = {
        'form': form,
        'author': author,
    }

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            url = reverse('viewprofile')
            return HttpResponseRedirect(url)

    return render(request, template, context)

def view_author_profile(request, author_id):
    author = Author.objects.get(id=author_id)

    form = ProfileForm(request.POST or None, request.FILES or None, instance=author)

    editable = (author.id == request.user.id)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            url = reverse('viewprofile')
            return HttpResponseRedirect(url)

    template = 'vue/profile.html'

    context = {
        'user_id': author.id,
        'form': form,
        'editable': editable
    }

    return render(request, template, context)

    # old view here
    # #The user who login in/use the application
    # # TODO: add cookie or token to store the user
    # user_author = request.user

    # author = Author.objects.get(id=author_id)
    # template = 'profiles/profiles_view.html'
    # # form = ProfileForm(instance=author)
    # status = True

    # if author == user_author:
    #     status = False
    # context = {
    #     'user_author': user_author,
    #     'author': author,
    #     'status': status,
    # }
    # return render(request, template, context)


def register(request):
    template = "login/register.html"
    
    if request.method == "POST":
        form = ProfileSignup(request.POST)
       
        if form.is_valid():
            print("...form is valid!")
            #Manually get host and format it.
            domain = "http://%s/" % request.get_host()

            #Calling form.save makes a valid instance of the author, but doesn't push to db
            #https://stackoverflow.com/a/20177911
            instance = form.save(commit=False)
            #Manually change host to that of the server.

            instance.host = domain
            #Save author object to database.
            instance.save()

            return redirect("/accounts/login")
        else:
            print("...form is INVALID!")
            print(form.errors)
            context = {
                'form': form,
            }
    else:
        form = ProfileSignup()
        context = {
            'form': form,
        }

    return render(request, template, context)


@login_required
def my_friends(request):

    author = request.user
    template = 'friends/friends_list.html'
    friendList = get_friend_profiles_of_author(author.url)

    context = {
        'author': author,
        'friendList': friendList,
    }

    return render(request, template, context)


@login_required
def my_friend_requests(request):

    author = request.user
    template = 'friends/friends_request.html'
    friendRequestList = get_friend_requests_to_author(author.url)
    context = {
        'author': author,
        'friendRequestList': friendRequestList,
    }

    return render(request, template, context)


@login_required
def my_friend_following(request):

    author = request.user
    template = 'friends/friends_follow.html'
    friendFollowList = get_friend_requests_from_author(author.url)

    context = {
        'author': author,
        'friendFollowList': friendFollowList,
    }

    return render(request, template, context)


@login_required
@csrf_exempt
def search_friends(request):

    author = request.user
    friendSearchList = Author.objects.none()
    template = 'friends/friends_search.html'

    if request.method == 'POST' and request.POST['search_text']:
        search_text = request.POST['search_text']
        friendSearchList = Author.objects.filter(displayName__contains=search_text) \
            | Author.objects.filter(firstName__contains=search_text) \
            | Author.objects.filter(lastName__contains=search_text)

    context = {
        'author': author,
        'friendSearchList': friendSearchList,
    }

    return render(request, template, context)


@login_required
def accept_friend(request, friend_id_to_accept):

    author = request.user
    friend = Author.objects.get(pk=friend_id_to_accept)

    if (friend and AuthorFriend.objects.filter(author=friend.url, friend=author.url)):
        AuthorFriend.objects.get_or_create(author=author.url, friend=friend.url)
    else:
        # invalid friend accept request
        pass
    return redirect('my_friends')


@login_required
def reject_friend(request, friend_id_to_reject):

    author = request.user
    friend = Author.objects.get(pk=friend_id_to_reject)

    if (friend and AuthorFriend.objects.filter(author=friend.url, friend=author.url)):
        AuthorFriend.objects.filter(author=friend.url, friend=author.url).delete()
    else:
        # invalid friend reject request
        pass
    return redirect('my_friends')
