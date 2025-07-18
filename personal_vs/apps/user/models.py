from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')

    must_change_password = models.BooleanField(default=False, verbose_name='Deve Alterar Senha',
                                               help_text='O usuário deve alterar a senha no próximo login.')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['username']


    def __str__(self):
        return self.username or self.email

    def get_absolute_url(self):
        return reverse_lazy('user:user:detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse_lazy('user:user:update', kwargs={'pk': self.pk})

    def get_change_password_url(self):
        return reverse_lazy('user:user:change_password', kwargs={'pk': self.pk})

    # TODO - Implementar. Atualmente retorna uma imagem padrão como placeholder.
    def get_avatar_url(self):
        return f'{settings.STATIC_URL}/img/person-avatar.png'

    def reset_password(self, password):
        self.set_password(password)
        self.must_change_password = True
        self.save()
        return True
