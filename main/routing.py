from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/<str:route>/', consumers.Consumer.as_asgi()),
    path('ws/<str:route>/<uuid>', consumers.JobTestConsumer.as_asgi()),
]