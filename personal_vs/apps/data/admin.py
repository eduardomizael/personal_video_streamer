from django.contrib import admin
from . import models


# @admin.register(models.Video)
# class VideoAdmin(admin.ModelAdmin):
#     fields = '__all__'
#
#
# @admin.register(models.MediaDirectory)
# class MediaDirectorAdmin(admin.ModelAdmin):
#     fields = '__all__'

admin.site.register(models.Video)
admin.site.register(models.MediaDirectory)