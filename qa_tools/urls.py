from django.urls import path

from qa_tools import views


urlpatterns = [
    path('', views.index, name='index'),
    path('brazeNotification/', views.braze_notification, name='braze_notification'),
    path('brazeNotification/<slug:project>', views.notification_detail, name='notification_detail'),

]