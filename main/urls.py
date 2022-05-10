from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^login/$', views.login_view, name='login'),
    re_path(r'^logout$', views.logout_view, name='logout'),
    re_path(r'^job/(?P<job_uuid>[0-9a-z-]+)/$', views.job, name='job'),
    re_path(r'^test/(?P<test_uuid>[0-9a-z-]+)/$', views.test, name='test'),
    re_path(r'^job_stop$', views.job_force_stop, name='job_force_stop')
]
