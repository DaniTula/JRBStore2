from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('firebase-test/', views.firebase_test, name='firebase_test'),
]
