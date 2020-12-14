from django.shortcuts import render, HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('qa_tool index page')