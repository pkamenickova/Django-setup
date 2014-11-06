from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile
from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import load_backend, BACKEND_SESSION_KEY

class OptionalRemoteUserMiddleware(RemoteUserMiddleware):
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            stored_backend = load_backend(request.session.get(BACKEND_SESSION_KEY, ''))
            if isinstance(stored_backend, RemoteUserBackend):
                request.META[self.header] = request.user.get_username()

        super(OptionalRemoteUserMiddleware, self).process_request(request)

        if request.user.is_authenticated():
            if request.META.get("REMOTE_USER_EMAIL", None):
                auth.authenticate(remote_user = request.user.get_username(),
                        attributes = {
                                'firstname' : request.META.get("REMOTE_USER_FIRSTNAME", None),
                                'lastname' : request.META.get("REMOTE_USER_LASTNAME", None),
                                'email' : request.META.get("REMOTE_USER_EMAIL", None),
                        })

class InterceptionRemoteUserMiddleware(object):
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            # request.META["REQUEST_METHOD"] = "GET"
            request.method = "GET"
