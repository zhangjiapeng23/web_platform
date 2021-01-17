from django.urls import path, re_path

from google_appstore_reviews import views

urlpatterns = [
    path('', views.nba_reviews_index, name='index'),
    re_path(r'detail/$', views.nba_reviews_detail, name='detail'),

]