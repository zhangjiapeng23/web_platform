from django.urls import path, re_path

from google_appstore_reviews import views

urlpatterns = [
    # path('', views.ReviewsProjectList.as_view(), name='index'),
    # re_path(r'(?P<project>\w+)/detail/$', views.reviews_project_detail, name='detail'),
    # re_path(r'(?P<project>\w+)/(?P<platform>\w+)/$', views.reviews_project_detail_api, name='project_detail_api'),
    # re_path(r'(?P<project>\w+)/$', views.reviews_project_index, name='project_index'),
    re_path(r'^projects/$', views.ProjectList.as_view(), name='project_list'),
    re_path(r'^projects/(?P<pk>[0-9]+)/$', views.Project.as_view(), name='project'),
    re_path(r'^reviews_info/$', views.ReviewInfoList.as_view(), name='review_info_list'),
    re_path(r'^reviews_detail/$', views.ReviewDetailList.as_view(), name='review_detail_list'),
    re_path(r'^reviews_detail/(?P<project_name>.*)/$', views.ReviewDetailProjectList.as_view(),
            name='review_detail_project_list')
    # re_path()
]