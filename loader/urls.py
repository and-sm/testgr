from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^loader$', views.loader, name='loader')
]
