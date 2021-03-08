import json
import re

from django.shortcuts import render, HttpResponse

from . import models

# Create your views here.

def index(request):
    # project build info index page.
    return render(request, 'project_info/index.html')


def android_project_list(request):
    return HttpResponse('it is android project list')


def android_project_detail(request, project):
    return HttpResponse('it is android {} project detail'.format(project))


def android_library_detail(request):
    return HttpResponse('it is android library detail')


def ios_project_list(request):
    return HttpResponse('it is iOS project list')


def ios_project_detail(request, project):
    return HttpResponse('it is iOS {} project detail'.format(project))


def ios_library_detail(request):
    return HttpResponse('it is iOS library detail')


