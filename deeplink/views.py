from django.shortcuts import render, HttpResponse

from deeplink import models


def index(request):
    projects = models.Project.objects.all()
    for i in projects:
        print(i.name)

    return render(request, 'deeplink/index.html', context={'projects': projects,
                                                            })


def list(request, project):
    return HttpResponse('%s deeplink list page' % project)