from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('videos/', views.VideoListView.as_view(), name='videos'),
]