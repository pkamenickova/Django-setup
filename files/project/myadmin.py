# /var/www/Django/project/project/myadmin.py:

from django.contrib.admin.sites import site as default_site

# http://stackoverflow.com/questions/4877335/how-to-use-custom-adminsite-class
class AdminSiteRegistryFix( object ):
    '''
    This fix links the '_registry' property to the orginal AdminSites
    '_registry' property. This is necessary, because of the character of
    the admins 'autodiscover' function. Otherwise the admin site will say,
    that you havn't permission to edit anything.
    '''

    def _registry_getter(self):
        return default_site._registry

    def _registry_setter(self,value):
        default_site._registry = value

    _registry = property(_registry_getter, _registry_setter)

from django.contrib.admin import AdminSite
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from functools import update_wrapper
from django.core.urlresolvers import reverse

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.admin.forms import AdminAuthenticationForm
from django.http import HttpResponseRedirect

from django.utils.translation import ugettext as _

class MyAdminSite(AdminSite, AdminSiteRegistryFix):

    def get_urls(self):
        from django.conf.urls import patterns, url

        urls = super(MyAdminSite, self).get_urls()
        urls = [
            url(r'^login/$', self.login, name='login'),
            url(r'^logout/$', self.logout, name='logout'),
        ] + urls
        return urls

    def admin_view(self, view, cacheable=False):
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse('admin:logout', current_app=self.name):
                    index_path = reverse('admin:index', current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse('admin:login', current_app=self.name)
                )
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    @never_cache
    def login(self, request, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        ### from django.contrib.auth import login as auth_login, authenticate
        if request.method == 'GET' and self.has_permission(request):
            # Already logged-in, redirect to admin index
            ### the_user = authenticate(remote_user=request.user)
            ### auth_login(request, the_user)
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)

        from django.contrib.auth.views import login
        context = {
            'title': _('Log in'),
            'app_path': request.get_full_path(),
        }
        if (REDIRECT_FIELD_NAME not in request.GET and
                REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = request.get_full_path()
        context.update(extra_context or {})

        defaults = {
            'extra_context': context,
            'current_app': self.name,
            'authentication_form': self.login_form or AdminAuthenticationForm,
            'template_name': self.login_template or 'admin/login.html',
        }
        return login(request, **defaults)

site = MyAdminSite()
