from django.urls import path

from deeplink import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/<slug:project>/', views.deeplink_list, name='deeplink_list'),
    path('edit/<slug:project>/', views.edit_project, name='deeplink_edit'),
    path('removeProject/', views.remove_project, name='remove_project'),
    path('modifyProject/', views.modify_project, name='modify_project'),
    path('removeDeeplink/', views.remove_deeplink, name='remove_deeplink'),
    path('modifyDeeplink/', views.modify_deeplink, name='modify_deeplink'),
]