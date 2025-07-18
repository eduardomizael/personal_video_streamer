"""
Backend de autenticação por email ao invés de username
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            if '@' in username:
                user = user_model.objects.get(email=username)
            else:
                user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
