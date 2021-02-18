import collections

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Count

from qa_tools import models
from qa_tools.tools.braze_notification import BrazePush
from qa_tools.tools.sdk_parse import SdkConfigParse
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

    return render(request, 'qa_tools/braze_notification/brazeNotification.html', context={'projects': project_list})


def notification_detail(request, project):
    response = dict()
    deeplink_type = models.Notification.objects.filter(project__name=project, push_type=1).all()
    push_type = models.Notification.objects.filter(project__name=project, push_type=0).all()
    general_type = models.Notification.objects.filter(project__name=project, push_type=2).all()
    response['deeplink'] = deeplink_type
    response['push_type'] = push_type
    response['general'] = general_type

    return render(request, 'qa_tools/braze_notification/notificationDetail.html', context={"project_name": project,
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
        elif not selected_items:
            response['msg'] = 'You must select a push item from below.'
        else:
            test_account = test_account.split(';')
            notifications = models.Notification.objects.filter(pk__in=selected_items).all()
            for notification in notifications:
                push_dict[notification.get_push_type_display()].append(notification.content)
            projcet_obj = models.Project.objects.filter(name=project_name).first()
            project_info['instance_url'] = projcet_obj.instance_url
            project_info['name'] = project_name
            project_info['scheme'] = projcet_obj.scheme
            project_info['api_key'] = projcet_obj.api_key
            project_info['test_account'] = test_account
            res = braze_notification_console(project_info, push_dict)
            response['code'] = 'success'
            response['msg'] = res


        return JsonResponse(response)


def braze_notification_console(project: dict, push: dict):
    instance_url = project.get('instance_url')
    deeplink_scheme = project.get('scheme')
    api_key = project.get('api_key')
    test_account = project.get('test_account')
    braze_push = BrazePush(instance_url=instance_url, api_key=api_key, deeplink_scheme=deeplink_scheme,
                           test_account=test_account)
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
        params = (item.upper() for item in params)
        braze_push.push_by_push_type(params)

    return braze_push.resp


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


def sdk_config(request):
    if request.method == 'GET':
        sdk_configs = models.SdkConifg.objects.all()

        return render(request, template_name='qa_tools/sdk_parse/sdk_config_list.html', context={'app_keys': sdk_configs})


def sdk_config_detail(request, appkey):
    if request.method == 'GET':
        sdk_config = SdkConfigParse()
        try:
            sdk_config.parse(appkey)
        except Exception as erro_msg:
            return render(request, template_name='qa_tools/sdk_parse/sdk_config_error.html',
                          context={'error_msg': erro_msg})

        else:
            return render(request, template_name='qa_tools/sdk_parse/sdk_config_detail.html',
                          context={'configurl': sdk_config.configurl,
                                   'configjson': sdk_config.text_decrypted_trim,
                                   'support': sdk_config.issupported,
                                   'comments': sdk_config.comments})

    elif request.method == 'POST':
        response = {'code': 'success', 'msg': None}
        project_name = request.POST.get("project_name")
        environment = request.POST.get("environment")
        is_exist = models.SdkConifg.objects.filter(app_key=appkey).first()
        if not is_exist:
            res = models.SdkConifg.objects.create(project_name=project_name, config_type=environment, app_key=appkey)
            if res:
                response['msg'] = 'App key add success.'
            else:
                response['code'] = 'fail'
                response['msg'] = 'App key add failed.'
        else:
            response['code'] = 'fail'
            response['msg'] = 'This app key already exists.'
        return JsonResponse(response)

    elif request.method == 'DELETE':
        response = {'code': 'success', 'msg': None}
        res = models.SdkConifg.objects.filter(app_key=appkey).delete()
        if res:
            response['msg'] = 'Delete success.'
        else:
            response['code'] = 'fail'
            response['msg'] = 'Delete failed.'
        return JsonResponse(response)

    elif request.method == 'PUT':
        pass
    else:
        print("not support this method.")

