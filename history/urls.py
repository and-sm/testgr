from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^history', views.history, name='history')
]
