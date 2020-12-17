from django.urls import path

from deeplink import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/<slug:project>/', views.deeplink_list, name='deeplink_list')

    
]