from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^management$', views.main, name='management'),
    url(r'^management/about$', views.about, name='about'),
    url(r'^api/env/change$', views.api_remap_env, name='api_remap_env'),
    url(r'^api/env/delete$', views.api_delete_env, name='api_delete_env')
]
