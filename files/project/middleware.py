from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile
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

class InterceptionRemoteUserMiddleware(object):
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            # request.META["REQUEST_METHOD"] = "GET"
            request.method = "GET"
