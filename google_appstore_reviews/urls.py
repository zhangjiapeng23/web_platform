from django.urls import path, re_path

from google_appstore_reviews import views

urlpatterns = [
    path('', views.ReviewsProjectList.as_view(), name='index'),
    re_path(r'(?P<project>\w+)/detail/$', views.reviews_project_detail, name='detail'),
    re_path(r'(?P<project>\w+)/(?P<platform>\w+)/$', views.reviews_project_detail_api, name='project_detail_api'),
    re_path(r'(?P<project>\w+)/$', views.reviews_project_index, name='project_index'),
]