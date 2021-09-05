from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from upload import views

urlpatterns = [
    path('upload/job/<uuid>/', views.UploadForJobView.as_view()),
    path('upload/test/<uuid>/', views.UploadForTestView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
