import json
import re


from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework import generics
from rest_framework import permissions

from mobile_QA_web_platform.settings.base import LOCAL_HOST as host
from mobile_QA_web_platform.settings.base import LOCAL_PORT as port
from .serializers import *
from mobile_QA_web_platform.utils.pagination import StandardResultsSetPagination

# Create your views here.


class ProjectAndroidList(generics.ListCreateAPIView):

    queryset = models.AndroidProject.objects.all()
    serializer_class = ProjectAndroidListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    ordering_fields = ('update_date',)


class ProjectAndroid(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.AndroidProject.objects.all()
    serializer_class = ProjectAndroidSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProjectIosList(generics.ListCreateAPIView):

    queryset = models.IosProject.objects.all()
    serializer_class = ProjectIOSListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    ordering_fields = ('update_date',)


class ProjectIos(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.IosProject.objects.all()
    serializer_class = ProjectIOSSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class BuildAndroidList(generics.ListAPIView):

    queryset = models.AndroidBuild.objects.all()
    serializer_class = BuildAndroidListSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project = self.kwargs['project']
        return models.AndroidBuild.objects.filter(project__project_name=project)


class BuildAndroid(generics.RetrieveDestroyAPIView):

    queryset = models.AndroidBuild.objects.all()
    serializer_class = BuildAndroidListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.AndroidBuild.objects.filter(project__project_name=project)


class BuildIosList(generics.ListAPIView):

    queryset = models.IosBuild.objects.all()
    serializer_class = BuildIosListSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project = self.kwargs['project']
        return models.IosBuild.objects.filter(project__project_name=project)


class BuildIos(generics.RetrieveDestroyAPIView):

    queryset = models.AndroidBuild.objects.all()
    serializer_class = BuildIosListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.IosBuild.objects.filter(project__project_name=project)







def index(request):
    # project build info index page.
    return render(request, 'project_info/index.html')


def android_project_list(request):
    android_projects = models.AndroidProject.objects.all().order_by('-update_date')
    data_format = request.GET.get('format')
    if data_format and data_format == "json":
        android_projects = list(android_projects.values())
        for item in android_projects:
            item['project_logo'] = host+ ':' + port + '/static/' + item['project_logo']

        return JsonResponse(android_projects, safe=False)
    return render(request, 'project_info/projects_list.html', context={'projects_list': android_projects,
                                                                       'platform': 'Android'})


def android_project_detail(request, project):
    page_size = int(request.GET.get('pageSize', 15))
    page = int(request.GET.get('page', 1))

    project_all = models.AndroidBuild.objects.filter(project=project)
    record_total = project_all.count()
    build_record_obj = project_all.order_by('-date').all()[(page - 1) * page_size:page * page_size]

    # get page index info
    total_pages = record_total // page_size + 1 if record_total % page_size else record_total // page_size
    start_page = page - 2 if page - 2 > 1 else 1
    end_page = start_page + 4 if start_page + 4 < total_pages else total_pages
    page_index = [index for index in range(start_page, end_page + 1)]

    # check include format param
    data_format = request.GET.get("format")
    if data_format and data_format == 'json':
        record_data = list(build_record_obj.values())
        for item in record_data:
            item['package_mapping_url'] = host+ ':' + port + item['package_mapping_url']

        resp = {"data": record_data,
                "page": page,
                "totalPage": total_pages,
                "pageSize": page_size}
        return JsonResponse(resp, safe=False)

    return render(request, 'project_info/android_project_detail.html', context={'build_record': build_record_obj,
                                                                        'total_pages': total_pages,
                                                                        'page_index': page_index,
                                                                        'project': project})


def android_library_detail(request):
    nid = request.GET.get('id')
    if nid:
        record_obj = models.AndroidBuild.objects.filter(nid=nid)
        library_list = record_obj.values_list('library_coordinate_list').first()[0]
        # serialize json obj to list obj
        library_list = json.loads(library_list)
        # sort snapshot library move to header
        change_index = 0
        for index, library in enumerate(library_list):
            if '-SNAPSHOT' in library['currentVersion']:
                library_list[change_index], library_list[index] = library_list[index], library_list[change_index]
                change_index += 1

        data_format = request.GET.get('format')
        if data_format == 'json':
            project_name = record_obj.values('project').first()['project']
            project_version = record_obj.values('package_version_name').first()['package_version_name']
            response = {
                'project_name': project_name,
                'project_version': project_version,
                'data': library_list
            }
            return JsonResponse(response, safe=False)

        return render(request, 'project_info/android_library_detail.html', context={'record': record_obj.first(),
                                                                                'library_list': library_list})


def ios_project_list(request):
    ios_projects = models.IosProject.objects.all().order_by('-update_date')
    data_format = request.GET.get("format")
    if data_format and data_format == 'json':
        ios_projects = list(ios_projects.values())
        for item in ios_projects:
            item['project_logo'] = host + ':' + port+'/static/' + item['project_logo']

        return JsonResponse(ios_projects, safe=False)
    return render(request, 'project_info/projects_list.html', context={'projects_list': ios_projects,
                                                                       'platform': 'iOS'})


def ios_project_detail(request, project):
    page_size = int(request.GET.get('pageSize', 15))
    page = int(request.GET.get('page', 1))

    project_all = models.IosBuild.objects.filter(project=project)
    record_total = project_all.count()
    build_record_obj = project_all.order_by('-date').all()[(page - 1) * page_size:page * page_size]

    # get page index info
    total_pages = record_total // page_size + 1 if record_total % page_size else record_total // page_size
    start_page = page - 2 if page - 2 > 1 else 1
    end_page = start_page + 4 if start_page + 4 < total_pages else total_pages
    page_index = [index for index in range(start_page, end_page + 1)]

    # check include format param
    data_format = request.GET.get("format")
    if data_format and data_format == 'json':
        record_data = list(build_record_obj.values())

        resp = {"data": record_data,
                "page": page,
                "totalPage": total_pages,
                "pageSize": page_size}
        return JsonResponse(resp, safe=False)

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

        data_format = request.GET.get('format')
        if data_format == 'json':
            project_name = record_obj.values('project').first()['project']
            project_version = record_obj.values('project_version').first()['project_version']
            response = {
                'project_name': project_name,
                'project_version': project_version,
                'data': library_list
            }
            return JsonResponse(response, safe=False)

        return render(request, 'project_info/ios_library_detail.html', context={'record': record_obj.first(),
                                                                                    'library_list': library_list})



