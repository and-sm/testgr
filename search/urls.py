from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^search$', views.search, name='search'),
    re_path(r'^search/filter$', views.filter_data, name='filter_data')
]
