from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^job/(?P<job_uuid>[0-9a-z-]+)/$', views.job, name='job'),
    url(r'^test/(?P<test_uuid>[0-9a-z-]+)/$', views.test, name='test')
]
