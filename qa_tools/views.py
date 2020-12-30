import collections

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Count

from qa_tools import models
from qa_tools.tools.braze_notification import BrazePush
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
    deeplink_type = models.Notification.objects.filter(project__name=project, push_type=1).all()
    push_type = models.Notification.objects.filter(project__name=project, push_type=0).all()
    general_type = models.Notification.objects.filter(project__name=project, push_type=2).all()
    response['deeplink'] = deeplink_type
    response['push_type'] = push_type
    response['general'] = general_type

    return render(request, 'qa_tools/notificationDetail.html', context={"project_name": project,
                                                                        "response": response,
                                                                        })


def send_braze_push(request):
    if request.is_ajax():
        response = {'code': 'fail', 'msg': None}
        push_dict = collections.defaultdict(list)
        project_info = dict()
        project_name = request.POST.get('project')
        selected_items = request.POST.getlist('selected_items[]')
        test_account = request.POST.get('test_account')
        if not test_account:
            response['msg'] = 'Test account is required.'
        else:
            notifications = models.Notification.objects.filter(pk__in=selected_items).all()
            for notification in notifications:
                push_dict[notification.get_push_type_display()].append(notification.content)
            projcet_obj = models.Project.objects.filter(name=project_name).first()
            project_info['instance_url'] = projcet_obj.instance_url
            project_info['name'] = project_name
            project_info['scheme'] = projcet_obj.scheme
            project_info['api_key'] = projcet_obj.api_key
            braze_notification_console(project_info, push_dict)

        return JsonResponse(response)


def braze_notification_console(project: dict, push: dict):
    instance_url = project.get('instance_url')
    deeplink_scheme = project.get('scheme')
    api_key = project.get('api_key')
    test_account = project.get('test_account')
    braze_push = BrazePush(instance_url=instance_url, api_key=api_key, deeplink_scheme=deeplink_scheme, test_account=test_account)
    general_type = push.get('general',  [])
    deeplink_type = push.get('deeplink', [])
    PUSH_TYPE_type = push.get('PUSH_TYPE',  [])

    for item in general_type:
        params = tuple(item.split(';'))
        braze_push.push_by_general(param=params)

    for item in deeplink_type:
        braze_push.push_by_deeplink(param=item)

    for item in PUSH_TYPE_type:
        params = tuple(item.split(';'))
        braze_push.push_by_push_type(params)



def add_push(request):
    if request.is_ajax():
        response = {'code': 'fail', 'msg': None, 'id': None}
        push_type_dict = {
            "deeplink": 1,
            "general": 2,
            "push_type": 0,
        }
        project_name = request.POST.get('project_name')
        push_type = request.POST.get('push_type')
        push_content = request.POST.get('push_content')
        if not push_content:
            response['msg'] = "It's required."
        else:
            project_obj = models.Project.objects.filter(name=project_name).first()
            res = models.Notification.objects.create(push_type=push_type_dict[push_type], content=push_content, project=project_obj)
            if res:
                response['code'] = 'success'
                response['msg'] = '%s add successful.' % res
                response['id'] = res.nid
            else:
                response['msg'] = 'Add push failed, please try again.'

        return JsonResponse(response)
            