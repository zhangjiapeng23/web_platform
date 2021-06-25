from django.urls import path, re_path
from django.views.generic.base import RedirectView

from deeplink import views

urlpatterns = [
    re_path(r'^projects/$', views.ProjectList.as_view(), name='project_list'),
    re_path(r'^projects/(?P<pk>[0-9]+)/$', views.Project.as_view(), name='project'),
    re_path(r'^deeplinks/(?P<project>[0-9a-zA-Z\_]+)/$',
            views.DeeplinkProjectList.as_view(), name="deeplink_list"),
    re_path(r'^deeplinks/(?P<project>[0-9a-zA-Z\_]+)/(?P<pk>[0-9]+)/$',
            views.DeeplinkProject.as_view(), name="deeplink"),

    # path('', views.index, name='index'),
    # re_path(r'^favicon\.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
    # path('list/NBADeeplinkSyncFromUS/', views.nba_sync_us, name='nba_sync_us'),
    # path('list/<slug:project>/', views.deeplink_list, name='deeplink_list'),
    # path('edit/<slug:project>/', views.add_deeplink, name='deeplink_edit'),
    # path('removeProject/', views.remove_project, name='remove_project'),
    # path('modifyProject/', views.modify_project, name='modify_project'),
    # path('removeDeeplink/', views.remove_deeplink, name='remove_deeplink'),
    # path('modifyDeeplink/', views.modify_deeplink, name='modify_deeplink'),
    
]