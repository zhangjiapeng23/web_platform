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


    return render(request, 'deeplink/index.html', context={'projects': projects,
                                                            })


def deeplink_list(request, project):
    project_boj = models.Project.objects.filter(name=project).first()
    contents = models.Contents.objects.filter(project__name=project).all().order_by('-create_time')
    scheme = project_boj.scheme
    full_deeplink = []
    for content in contents:
        full_deeplink.append(scheme + '://' + content.body)
    return render(request, 'deeplink/list.html', context={'project': project_boj,
                                                          'full_deeplink': full_deeplink,
                                                          })


def edit_project(request, project):
    project_obj = models.Project.objects.filter(name=project).first()
    scheme = project_obj.scheme

    if request.is_ajax():
        response = {'code': 'fail', 'msg': {}}
        body = request.POST.get('body')
        if not body:
            response['msg']['error'] = 'Deeplink content is required.'
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
            response['msg']= '%s project delete failed.' % prject_name
            return JsonResponse(response)



def modify_project(request):

    return HttpResponse('modify project' )


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

    return HttpResponse('deeplink modify')