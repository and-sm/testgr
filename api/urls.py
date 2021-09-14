from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('api/environment/<pk>/', views.Environment.as_view()),
    path('api/job/<uuid>/', views.Job.as_view()),
    path('api/tstorage/<pk>/', views.TestsStorageItem.as_view()),
    path('api/bugs/<pk>/', views.BugItem.as_view()),
    path('api/bugs/change/<pk>/', views.BugsManagement.as_view()),
    path('api/user/<pk>/', views.Users.as_view()),
    path('api/user/<pk>/regenerate-token', views.UsersRegenerateToken.as_view()),
    path('api/settings/', views.SettingsView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
