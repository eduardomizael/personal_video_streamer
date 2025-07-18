from django.urls import path, include
from . import views

app_name = 'data'


video_patterns = ([
    path('', views.VideoListView.as_view(), name='list'),
    path('<int:pk>/', views.VideoPlayerView.as_view(), name='player'),
    path('stream/<int:pk>/', views.stream_video, name='stream'),

], 'video')

urlpatterns = [
    path('video/', include(video_patterns, 'video')),
]
