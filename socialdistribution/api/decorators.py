import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .utils import authenticate_server

#############################################################################
# Check first if a user object is authenticated, then check if basic auth
# supplied and valid. Otherwise return 403.
#
# Attribution: https://djangosnippets.org/snippets/243/
#############################################################################
def check_auth(view):
    def view_or_basicauth(request, *args, **kwargs):
        """
        Check first is user is logged in and authenticated
        """
        if request.user.is_authenticated:
            # Already logged in, just return the view.
            return view(request, *args, **kwargs)

        # They are not logged in. See if they provided HTTP BASIC AUTH credentials
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':', 1)

                if authenticate_server(username=uname, password=passwd):
                    request.server_id = uname
                    return view(request, *args, **kwargs)

                # Check if user exists
                user = authenticate(username=uname, password=passwd)
                # If user exists, and is active, login user and then check that they're authenticated, then return view
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        if request.user.is_authenticated:
                            return view(request, *args, **kwargs)
                response = HttpResponse()
                response.status_code = 401
                response['WWW-Authenticate'] = 'Basic'
                return response
        else:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic'
            return response

        # If request does not have active user, or not HTTP Basic Auth, return 403.
        response = HttpResponse()
        response.status_code = 403

        return response

    return view_or_basicauth
