from django.urls import path, re_path

from qa_tools import views


urlpatterns = [
    path('', views.index, name='index'),
    path('brazeNotification/', views.braze_notification, name='braze_notification'),
    path('brazeNotification/<slug:project>', views.notification_detail, name='notification_detail'),
    path('sendBrazePush/', views.send_braze_push, name='send_braze_push'),
    path('addPush/', views.add_push, name='addPush'),
    path('sdkconfig/', views.sdk_config, name='sdk_config'),
    path('sdkconfig/<path:appkey>', views.sdk_config_detail, name='sdk_config_detail'),

]