from django.urls import path

from google_appstore_reviews import views

urlpatterns = [
    path('', views.nba_reviews_index, name='index'),

]