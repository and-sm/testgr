from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^search$', views.search, name='search'),
    url(r'^search/filter$', views.filter_data, name='filter_data')
]
