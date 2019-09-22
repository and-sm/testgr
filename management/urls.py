from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^management$', views.main, name='management'),
    url(r'^management/about$', views.about, name='about'),
    url(r'^management/users$', views.users, name='users'),
    url(r'^management/users/add$', views.users_add, name='users_add'),
]
