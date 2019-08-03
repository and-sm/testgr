from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^management$', views.main, name='management'),
    url(r'^management/about$', views.about, name='about'),
]
