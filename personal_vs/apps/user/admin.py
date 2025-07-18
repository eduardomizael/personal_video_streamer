from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# admin.site.register(User, UserAdmin)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}))

