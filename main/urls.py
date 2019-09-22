from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^job/(?P<job_uuid>[0-9a-z-]+)/$', views.job, name='job'),
    url(r'^test/(?P<test_uuid>[0-9a-z-]+)/$', views.test, name='test'),
    url(r'^job_stop$', views.job_force_stop, name='job_force_stop')
]
