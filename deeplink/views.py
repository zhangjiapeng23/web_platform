import re

from collections import defaultdict
import requests
from lxml import etree

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import *


class ProjectList(generics.ListCreateAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class Project(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes(IsAuthenticatedOrReadOnly,)


class DeeplinkProjectList(generics.ListCreateAPIView):

    queryset = models.Contents.objects.all()
    serializer_class = DeeplinkContentCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.Contents.objects.filter(project__name=project)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DeeplinkContentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DeeplinkContentListSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        body = self.request.data['body']
        classification = self.get_classification(body)
        project_instance = models.Project.objects.get(name=self.kwargs['project'])
        serializer.save(project=project_instance, classification=classification )

    def get_classification(self, body):
        _body = body.split('/')
        if len(_body) > 1:
            if _body[0].startswith('http'):
                return 'branch'
            return _body[0]
        return 'default'


class DeeplinkProject(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.Project.objects.all()
    serializer_class = DeeplinkSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        project = self.kwargs['project']
        return models.Contents.objects.filter(project__name=project)

    def perform_update(self, serializer):
        project_instance = models.Project.objects.get(name=self.kwargs['project'])
        body = self.request.data.get('body')
        if body is not None:
            classification = self.get_classification(body)
            serializer.save(project=project_instance, classification=classification)
        serializer.save(project=project_instance)

    def get_classification(self, body):
        _body = body.split('/')
        if len(_body) > 1:
            if _body[0].startswith('http'):
                return 'branch'
            return _body[0]
        return 'default'

@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def index(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_scheme = request.POST.get('project_scheme')
        response = {'code': 'fail', 'msg': None}

        if not project_name or not project_scheme:
            response['msg'] = "Project name and scheme are required."
        elif models.Project.objects.filter(name=project_name):
            response['msg'] = "Current project name is created, please change a name."
        else:
            project_obj = models.Project.objects.create(name=project_name, scheme=project_scheme)
            response['code'] = 'success'
            response['msg'] = 'Project %s create successful.' % project_name
            response['data'] = {
                'nid': project_obj.nid,
                'name': project_obj.name,
                'scheme': project_obj.scheme
            }
        return JsonResponse(response)

    projects = models.Project.objects.all()
    data_format = request.GET.get('format')
    if data_format == 'json':
        projects = list(projects.values())
        return JsonResponse(projects, safe=False)

    return render(request, 'deeplink/index.html', context={'projects': projects, })


def deeplink_list(request, project):
    if request.method == 'GET':
        set_grouping = request.GET.get('grouping', default='true')
        project_obj = models.Project.objects.filter(name=project).first()
        if project_obj:
            contents = models.Contents.objects.filter(project__name=project).all().order_by('-create_time')
            scheme = project_obj.scheme + '://'
            project_id = project_obj.nid

            # grounping
            if set_grouping == 'true':
                project_dict = defaultdict(list)
                for content in contents:
                    classification = content.classification
                    if classification == 'Branch':
                        deeplink_path = content.body
                    else:
                        deeplink_path = scheme + content.body
                    deeplink_dict = {'id': content.nid,
                                     'content': deeplink_path,
                                     'body': content.body}
                    project_dict[content.classification].append(deeplink_dict)

                data_format = request.GET.get('format')
                if data_format == 'json':
                    response = {
                        'project': project,
                        'id': project_id,
                        'scheme': scheme,
                        'data': project_dict
                    }
                    return JsonResponse(response, safe=False)

                return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                    'set_grouping': set_grouping,
                                                                    'full_deeplink_group': project_dict,
                                                                    })
            else:
                # not grouping
                full_deeplink = []
                for content in contents:
                    if content.classification == 'Branch':
                        full_deeplink.append(content.body)
                    else:
                        full_deeplink.append(scheme + content.body)
                return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                        'set_grouping': set_grouping,
                                                                        'full_deeplink': full_deeplink,
                                                                        })
    return HttpResponse('404')


def add_deeplink(request, project):
    project_obj = models.Project.objects.filter(name=project).first()
    scheme = project_obj.scheme + '://'

    if request.method == 'POST':
        response = {'code': 'fail', 'msg': {}}
        body = request.POST.get('body')
        if not body:
            response['msg']['error'] = 'Deeplink content is required.'
        else:
            body_slice = re.split(r'[/?]', body)
            if (len(body_slice) > 1):
                classification = body_slice[0]
                if classification == 'https:':
                    classification = 'Branch'
                    scheme = ''
                res_obj = models.Contents.objects.create(body=body, classification=classification, project=project_obj)
            else:
                res_obj = models.Contents.objects.create(body=body, project=project_obj)
            response['code'] = 'success'
            response['msg']['deeplink'] = scheme + body
            response['msg']['nid'] = res_obj.nid
            response['msg']['body'] = body
        return JsonResponse(response)

    contents = models.Contents.objects.filter(project=project_obj).all().order_by('-create_time')
    full_deeplink = []
    for content in contents:
        classification =  content.classification
        _deeplink = {}
        _deeplink['deeplink'] = content.body if classification == 'Branch' else scheme + content.body
        _deeplink['body'] = content.body
        _deeplink['nid'] = content.nid
        _deeplink['classification'] = classification
        full_deeplink.append(_deeplink)

    return render(request, 'deeplink/edit.html', context={'project': project_obj,
                                                          'full_deeplink': full_deeplink,
                                                          })


def remove_project(request):
    if request.method == 'POST':
        response = {'code': 'fail', 'msg': None}
        project_name = request.POST.get('project')
        res = models.Project.objects.filter(name=project_name).delete()
        if res:
            response['code'] = 'success'
            response['msg'] = '%s project delete successful.' % project_name
            return JsonResponse(response)
        else:
            response['msg'] = '%s project delete failed.' % project_name
            return JsonResponse(response)


def modify_project(request):
    if request.method == 'POST':
        response = {'code': 'fail', 'msg': None}
        scheme = request.POST.get('scheme')
        nid = request.POST.get('nid')
        if not scheme:
            response['msg'] = 'Scheme is required.'
        else:
            res = models.Project.objects.filter(nid=nid).update(scheme=scheme)
            if res:
                response['code'] = 'success'
                response['msg'] = 'Project scheme modify successful.'

        return JsonResponse(response)


def remove_deeplink(request):
    if request.method == 'POST':
        response = {'code': 'fail', 'msg': None}
        deeplink_id = request.POST.get('nid')
        res = models.Contents.objects.filter(nid=deeplink_id).delete()
        if res:
            response['code'] = 'success'
            response['msg'] = 'Remove successful.'
            return JsonResponse(response)
        else:
            response['msg'] = 'Remove failed.'
            return JsonResponse(response)


def modify_deeplink(request):
    if request.method == 'POST':
        response = {'code': 'fail', 'msg': None}
        deeplink_id = request.POST.get('deeplink_id')
        deeplink_body = request.POST.get('deeplink_body')
        if not deeplink_body:
            response['msg'] = 'Deeplink content is required.'
        else:
            deeplink_item = models.Contents.objects.filter(nid=deeplink_id).all()
            body_alice = re.split(r'[/?]', deeplink_body)
            if (len(body_alice) > 1):
                if body_alice[0] == 'https:':
                    res = deeplink_item.update(body=deeplink_body, classification='Branch')
                    scheme = ''
                else:
                    res = deeplink_item.update(body=deeplink_body, classification=body_alice[0])
                    scheme = deeplink_item[0].project.scheme + '://'
            else:
                res = deeplink_item.update(body=deeplink_body, classification='Default')
                scheme = deeplink_item[0].project.scheme + '://'
            if res:
                response['code'] = 'success'
                response['msg'] = scheme + deeplink_body
            else:
                response['msg'] = 'Modify fail. Please try again.'

        return JsonResponse(response)


def nba_sync_us(request):
    if request.method == 'GET':
        project_obj = NBASyncUs()
        project_obj.name = 'NBA Deeplink Sync From US'
        set_grouping = request.GET.get('grouping', default='true')
        resp = requests.get('http://neulion-a.akamaihd.net/nlmobile/nba/deeplinks.htm')
        doc = etree.HTML(resp.text)
        deeplinks = doc.xpath('//a/@href')
        o = re.compile(r'^gametime.*|^https://app.link.nba.com.*')
        deeplink_list = [item for item in deeplinks if o.search(item)]
        if set_grouping == 'true':
            deeplink_dict = defaultdict(list)
            for deeplink in deeplink_list:
                if re.search(r'^https://app.link.nba.com.*', deeplink):
                    deeplink_dict['Branch'].append(deeplink)
                else:
                    body = re.match(r'^gametime://(.*)', deeplink)
                    if body:
                        body_slice = re.split(r'[/?]', body[1])
                        if len(body_slice) > 1:
                            deeplink_dict[body_slice[0]].append(deeplink)
                        else:
                            deeplink_dict['Default'].append(deeplink)

            data_format = request.GET.get('format')
            if data_format == 'json':
                return JsonResponse(deeplink_dict, safe=False)

            return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                    'set_grouping': set_grouping,
                                                                    'full_deeplink_group': deeplink_dict,
                                                                    })
        else:
            return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                        'set_grouping': set_grouping,
                                                                        'full_deeplink': deeplink_list,
                                                                        })


class NBASyncUs:
    """
    support nba_sync_us to provide a project instance to html model.
    """
    name = 'nba_sync_us'
    
    def __str__(self):
        return self.name.replace(' ', '')
