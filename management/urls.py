from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^management$', views.main, name='management'),
    re_path(r'^management/about$', views.about, name='about'),
    re_path(r'^management/users$', views.users, name='users'),
    re_path(r'^management/users/add$', views.users_add, name='users_add'),
    re_path('management/users/edit/<pk>/', views.users_edit, name='users_edit'),
    re_path(r'^management/settings$', views.settings, name='settings'),
]
