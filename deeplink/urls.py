from django.urls import path

from deeplink import views

urlpatterns = [
    path('', views.index, name='index'),
    
]