
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from qa_tools import models
# Create your views here.

def index(request):

    return render(request, 'qa_tools/index.html')


def braze_notification(request):
    if request.is_ajax():
        response = {'code': 'fail','msg': None}
        project_name = request.POST.get('project_name')
        project_scheme = request.POST.get('project_scheme')
        api_key = request.POST.get('project_api_key')
        instance_url = request.POST.get('project_instance_url')
        res = models.Project.objects.filter(name=project_name)
        if not project_name:
            response['msg'] = 'Porject name is required.'
        elif not project_scheme:
            response['msg'] = 'Project scheme is required.'
        elif not api_key:
            response['msg'] = 'Project api_key is required.'
        elif not instance_url:
            response['msg'] = 'Project instance_url is required.'
        else:
            if res:
                response['msg'] = '%s project name is used, Please input again.' % project_name
            else:
                res = models.Project.objects.create(name=project_name, scheme=project_scheme, api_key=api_key, instance_url=instance_url)
                if res:
                    response['code'] = 'success'
                    response['msg'] = 'Create %s project successful.'
                else:
                    response['msg'] = 'Create %s project failed, please try again.'
        return JsonResponse(response)

    project_list = list(models.Project.objects.all())

    return render(request, 'qa_tools/brazeNotification.html', context={'projects': project_list})


def notification_detail(request, project):
    response = dict()
    deeplink_type = models.Notification.objects.filter(project__name=project, type=1).all()
    push_type = models.Notification.objects.filter(project__name=project, type=0).all()
    general_type = models.Notification.objects.filter(project__name=project, type=2).all()
    response['deeplink'] = deeplink_type
    response['push_type'] = push_type
    response['general'] = general_type

    return render(request, 'qa_tools/notificationDetail.html', context={"project_name": project,
                                                                        "response": response,
                                                                        })