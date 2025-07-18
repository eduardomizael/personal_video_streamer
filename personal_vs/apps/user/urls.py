from django.urls import path, include

from . import views

user_patterns = ([
    path('', views.UserListView.as_view(), name='list'),
    # path('add/', views.StationListView.as_view(), name='create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('<int:pk>/change/', views.UserUpdateView.as_view(), name='update'),
    path('<int:pk>/change_password/', views.UserPasswordChangeView.as_view(), name='change_password'),

], 'user')


app_name = 'user'
urlpatterns = [
    path('user/', include(user_patterns, namespace='user')),

]
