from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^api/jobs/latest$', views.jobs_latest, name='jobs_latest'),
    url(r'^api/jobs/running$', views.jobs_running, name='jobs_running'),
    url(r'^api/jobs/running_count$', views.jobs_running_count, name='jobs_running_count'),
    url(r'^api/job/details$', views.job_details, name='job_details')
]