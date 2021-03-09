import json
import re

from django.shortcuts import render, HttpResponse

from . import models

# Create your views here.

def index(request):
    # project build info index page.
    return render(request, 'project_info/index.html')


def android_project_list(request):
    android_projects = models.AndroidProject.objects.all()
    return render(request, 'project_info/projects_list.html', context={'projects_list': android_projects,
                                                                       'platform': 'Android'})


def android_project_detail(request, project):
    page_size = request.GET.get('pageSize', 10)
    page = request.GET.get('page', 1)

    project_all = models.AndroidBuild.objects.filter(project=project)
    record_total = project_all.count()
    build_record_obj = project_all.order_by('-date').all()[(page - 1) * page_size:page * page_size]

    # get page index info
    total_pages = record_total // page_size + 1 if record_total % page_size else record_total // page_size
    start_page = page - 2 if page - 2 > 1 else 1
    end_page = start_page + 4 if start_page + 4 < total_pages else total_pages
    page_index = [index for index in range(start_page, end_page + 1)]



    return render(request, 'project_info/android_project_detail.html', context={'build_record': build_record_obj,
                                                                        'total_pages': total_pages,
                                                                        'page_index': page_index,
                                                                        'project': project})


def android_library_detail(request):
    nid = request.GET.get('id')
    if nid:
        record_obj = models.AndroidBuild.objects.filter(nid=nid)
        library_list= record_obj.values_list('library_coordinate_list').first()[0]
        # serialize json obj to list obj
        library_list = json.loads(library_list)
        # sort snapshot library move to header
        change_index = 0
        for index, library in enumerate(library_list):
            if '-SNAPSHOT' in library['currentVersion']:
                library_list[change_index], library_list[index] = library_list[index], library_list[change_index]
                change_index += 1

        return render(request, 'project_info/android_library_detail.html', context={'record': record_obj.first(),
                                                                                'library_list': library_list})


def ios_project_list(request):
    ios_projects = models.IosProject.objects.all()
    return render(request, 'project_info/projects_list.html', context={'projects_list': ios_projects,
                                                                       'platform': 'iOS'})


def ios_project_detail(request, project):
    page_size = request.GET.get('pageSize', 10)
    page = request.GET.get('page', 1)

    project_all = models.IosBuild.objects.filter(project=project)
    record_total = project_all.count()
    build_record_obj = project_all.order_by('-date').all()[(page - 1) * page_size:page * page_size]

    # get page index info
    total_pages = record_total // page_size + 1 if record_total % page_size else record_total // page_size
    start_page = page - 2 if page - 2 > 1 else 1
    end_page = start_page + 4 if start_page + 4 < total_pages else total_pages
    page_index = [index for index in range(start_page, end_page + 1)]

    return render(request, 'project_info/ios_project_detail.html', context={'build_record': build_record_obj,
                                                                                'total_pages': total_pages,
                                                                                'page_index': page_index,
                                                                                'project': project})


def ios_library_detail(request):
    nid = request.GET.get('id')
    if nid:
        record_obj = models.IosBuild.objects.filter(nid=nid)
        library_list = record_obj.values_list('framework').first()[0]
        # serialize json obj to list obj
        library_list = json.loads(library_list)
        # sort snapshot library move to header
        change_index = 0
        for index, library in enumerate(library_list):
            if re.match(r'\d+\.\d+\.0\d+', library['frameworkVersion']) \
                    or 'x' in str(library['frameworkVersion']):
                library_list[change_index], library_list[index] = library_list[index], library_list[change_index]
                change_index += 1

        return render(request, 'project_info/ios_library_detail.html', context={'record': record_obj.first(),
                                                                                    'library_list': library_list})



