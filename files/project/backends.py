from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.backends import RemoteUserBackend


class MyRemoteUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
