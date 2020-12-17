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
    for i in projects:
        print(i.name)

    return render(request, 'deeplink/index.html', context={'projects': projects,
                                                            })


def deeplink_list(request, project):
    contents = models.Contents.objects.filter(project__name=project).all()
    return render(request, 'deeplink/list.html', context={'project': project,
                                                          'contents': contents,
                                                          })


def edit_project(request, project):

    return render(request, 'deeplink/edit.html', context={'project': project})


def remove_project(request, project):

    return HttpResponse('%s remove' % project)
