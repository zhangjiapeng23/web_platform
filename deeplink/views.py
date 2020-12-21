import re

from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from deeplink import models


def index(request):
    if request.is_ajax():
        project_name = request.POST.get('project_name')
        project_scheme = request.POST.get('project_scheme')
        response = {'code': 'fail', 'msg': None}

        if not project_name or not project_scheme:
            response['msg'] = "Project name and scheme are required."
        elif models.Project.objects.filter(name=project_name):
            response['msg'] = "Current project name is created, please change a name."
        else:
            models.Project.objects.create(name=project_name, scheme=project_scheme)
            response['code'] = 'success'
            response['msg'] = 'Project %s create successful.'
        return JsonResponse(response)

    projects = models.Project.objects.all()

    return render(request, 'deeplink/index.html', context={'projects': projects, })


def deeplink_list(request, project):
    if request.method == 'GET':
        set_grouping = request.GET.get('grouping', default='true')
        project_obj = models.Project.objects.filter(name=project).first()
        if project_obj:
            contents = models.Contents.objects.filter(project__name=project).all().order_by('-create_time')
            scheme = project_obj.scheme
            # grounping
            if set_grouping == 'true':
                project_dict = defaultdict(list)
                for content in contents:
                    deeplink_path = scheme + '://' + content.body 
                    project_dict[content.classification].append(deeplink_path)
                return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                    'set_grouping': set_grouping,
                                                                    'full_deeplink_group': project_dict,
                                                                    })
            else:
                # not grouping
                full_deeplink = []
                for content in contents:
                    full_deeplink.append(scheme + '://' + content.body)
                return render(request, 'deeplink/list.html', context={'project': project_obj,
                                                                        'set_grouping': set_grouping,
                                                                        'full_deeplink': full_deeplink,
                                                                        })
    return HttpResponse('404')


def add_deeplink(request, project):
    project_obj = models.Project.objects.filter(name=project).first()
    scheme = project_obj.scheme

    if request.is_ajax():
        response = {'code': 'fail', 'msg': {}}
        body = request.POST.get('body')
        if not body:
            response['msg']['error'] = 'Deeplink content is required.'
        else:
            body_alice = re.split(r'[/?]', body)
            if (len(body_alice) > 1):
                classification = body_alice[0]
                res_obj = models.Contents.objects.create(body=body, classification=classification, project=project_obj)
            else:
                res_obj = models.Contents.objects.create(body=body, project=project_obj)
            response['code'] = 'success'
            response['msg']['deeplink'] = scheme + '://' + body
            response['msg']['nid'] = res_obj.nid
        return JsonResponse(response)

    contents = models.Contents.objects.filter(project=project_obj).all().order_by('-create_time')
    full_deeplink = []
    for content in contents:
        _deeplink = {}
        _deeplink['deeplink'] = scheme + '://' + content.body
        _deeplink['body'] = content.body
        _deeplink['nid'] = content.nid
        _deeplink['classification'] = content.classification
        full_deeplink.append(_deeplink)

    return render(request, 'deeplink/edit.html', context={'project': project_obj,
                                                          'full_deeplink': full_deeplink,
                                                          })


def remove_project(request):
    if request.is_ajax():
        response = {'code': 'fail', 'msg': None}
        prject_name = request.POST.get('project')
        res = models.Project.objects.filter(name=prject_name).delete()
        if res:
            response['code'] = 'success'
            response['msg'] = '%s project delete successful.' % prject_name
            return JsonResponse(response)
        else:
            response['msg'] = '%s project delete failed.' % prject_name
            return JsonResponse(response)


def modify_project(request):
    if request.is_ajax():
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
    if request.is_ajax():
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
    if request.is_ajax():
        response = {'code': 'fail', 'msg': None}
        deeplink_id = request.POST.get('deeplink_id')
        deeplink_body = request.POST.get('deeplink_body')
        if not deeplink_body:
            response['msg'] = 'Deeplink content is required.'
        else:
            deeplink_item = models.Contents.objects.filter(nid=deeplink_id).all()
            body_alice = re.split(r'[/?]', deeplink_body)
            if (len(body_alice) > 1):
                res = deeplink_item.update(body=deeplink_body, classification=body_alice[0])
            else:
                res = deeplink_item.update(body=deeplink_body, classification='Default')
            scheme = deeplink_item[0].project.scheme
            if res:
                response['code'] = 'success'
                response['msg'] = scheme + '://' + deeplink_body
            else:
                response['msg'] = 'Modify fail. Please try again.'

        return JsonResponse(response)