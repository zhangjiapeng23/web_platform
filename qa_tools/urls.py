from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView

from qa_tools import views


urlpatterns = [
    re_path(r'^projects/$', views.ProjectList.as_view(), name='project_list'),
    re_path(r'^projects/(?P<pk>[0-9]+)/$', views.Project.as_view(), name='project'),
    re_path(r'^notifications/(?P<project>[0-9a-zA-Z]+)/$',
            views.NotificationList.as_view(), name='notification_list'),
    path('', views.index, name='index'),
    path('brazeNotification/', views.braze_notification, name='braze_notification'),
    path('brazeNotification/delete/', views.braze_notification_delete, name='braze_notification_delete_project'),
    path('brazeNotification/<slug:project>', views.notification_detail, name='notification_detail'),
    path('sendBrazePush/', views.send_braze_push, name='send_braze_push'),
    path('addPush/', views.add_push, name='addPush'),
    path('sdkconfig/', views.sdk_config, name='sdk_config'),
    path('sdkconfig/<path:appkey>', views.sdk_config_detail, name='sdk_config_detail'),
    path('NLiOS/', views.ios_upload_api, name='ios_upload_api'),
    path('NLAndroid/', views.android_upload_api, name='android_upload_api'),
    path('NLAndroid/upload/', views.android_mapping_upload_api, name='android_mapping_upload_api'),
    re_path('^localizationtool/$', views.localization_tool, name='localization_tool'),
    re_path('^localizationUpload/$', views.localization_upload, name='localization_upload'),
]