from django.shortcuts import render

# Create your views here.


def nba_reviews_index(request):

    return render(request, 'google_appstore_reviews/nba_reviews_index.html')
