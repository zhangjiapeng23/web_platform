from django.urls import path

from qa_tools import views


urlpatterns = [
    path('', views.index, name='index'),
    
]