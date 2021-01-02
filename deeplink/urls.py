from django.urls import path, re_path
from django.views.generic.base import RedirectView

from deeplink import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
    path('list/NBADeeplinkSyncFromUS/', views.nba_sync_us, name='nba_sync_us'),
    path('list/<slug:project>/', views.deeplink_list, name='deeplink_list'),
    path('edit/<slug:project>/', views.add_deeplink, name='deeplink_edit'),
    path('removeProject/', views.remove_project, name='remove_project'),
    path('modifyProject/', views.modify_project, name='modify_project'),
    path('removeDeeplink/', views.remove_deeplink, name='remove_deeplink'),
    path('modifyDeeplink/', views.modify_deeplink, name='modify_deeplink'),
    
]