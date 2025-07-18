from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from . import models


class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.TextInput())


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = models.User
        fields = ('email', 'password1', 'password2')


class UserForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False, label='Ativo', initial=True,
                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta:
        model = models.User
        fields = ['username', 'email', 'password', 'is_active', 'available_stations', 'actual_station']

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        passwd = self.cleaned_data.get('password')
        user.set_password(passwd)
        if commit:
            user.save()
        return user


class PasswordChangeForm(auth_forms.PasswordChangeForm):

    def save(self, **kwargs):
        user = self.user
        user.set_password(self.cleaned_data["new_password1"])
        user.must_change_password = False
        user.save()
        return user
