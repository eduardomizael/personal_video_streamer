from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.views import generic as views
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.conf import settings

from . import forms

User = get_user_model()


class UserListView(views.ListView):
    model = settings.AUTH_USER_MODEL
    template_name = 'user/user_list.html'
    paginate_by = 100


class UserDetailView(views.DetailView):
    model = settings.AUTH_USER_MODEL
    template_name = 'user/user_detail.html'

    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(views.UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'user/user_update.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return self.object.get_absolute_url()


class UserPasswordChangeView(PermissionRequiredMixin, PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'user/password_change.html'
    permission_required = 'user.change_user'
    object = None

    def get_success_url(self):
        return self.object.get_change_url()

    def get_context_data(self, **kwargs):
        context = super(UserPasswordChangeView, self).get_context_data(**kwargs)
        # context['object'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super(UserPasswordChangeView, self).get_form_kwargs()
        # user_id = self.kwargs.get('pk', None)
        # self.object = UserEx.objects.get(pk=user_id)
        # kwargs['user'] = self.object
        return kwargs
