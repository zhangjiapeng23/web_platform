import collections
import json
import os
import re

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from werkzeug.utils import secure_filename
from django.middleware.csrf import get_token

from qa_tools import models
from qa_tools.tools.braze_notification import BrazePush
from qa_tools.tools.sdk_parse import SdkConfigParse
from qa_tools.tools.localization_tool import localization_value2number
from project_info import models as project_info_models
from mobile_QA_web_platform.settings import MEDIA_ROOT
# Create your views here.


def index(request):

    return render(request, 'qa_tools/index.html')


def braze_notification(request):
    if request.method == 'POST':
        response = {'code': 'fail', 'msg': None}
        project_name = request.POST.get('project_name')
        project_scheme = request.POST.get('project_scheme')
        api_key = request.POST.get('project_api_key')
        instance_url = request.POST.get('project_instance_url')
        res = models.Project.objects.filter(name=project_name)
        if not project_name:
            response['msg'] = 'Project name is required.'
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
                print(type(res))
                print(res)
                if res:
                    response['code'] = 'success'
                    response['msg'] = 'Create %s project successful.' % project_name
                    response['data'] = {'nid': res.nid,
                                        'name':res.name,
                                        'scheme': res.scheme,
                                        'api_key': res.api_key,
                                        'instance_url': res.instance_url}
                else:
                    response['msg'] = 'Create %s project failed, please try again.'
        return JsonResponse(response)

    project_list = models.Project.objects.all()
    data_format = request.GET.get("format")
    if data_format == 'json':
        project_list = list(project_list.values())
        return JsonResponse(project_list, safe=False)

    project_list = list(project_list)
    return render(request, 'qa_tools/braze_notification/brazeNotification.html', context={'projects': project_list})


def braze_notification_delete(request):
    if request.method == 'POST':
        response = {'code': 'failed', 'msg': ''}
        nid = request.POST.get('nid')
        if not nid:
            response['msg'] = 'Project id is required.'
        else:
            res = models.Project.objects.filter(nid=nid).first()
            if not res:
                response['msg'] = 'Not find this project, please check again.'
            else:
                res.delete()
                response['code'] = 'success'
                response['msg'] = 'Project %s delete success.' % res.name

        return JsonResponse(response, safe=False)


def notification_detail(request, project):
    response = dict()
    deeplink_type = models.Notification.objects.filter(project__name=project, push_type=1).all()
    push_type = models.Notification.objects.filter(project__name=project, push_type=0).all()
    general_type = models.Notification.objects.filter(project__name=project, push_type=2).all()


    data_format = request.GET.get('format')
    if data_format == 'json':
        response['deeplink'] = list(deeplink_type.values())
        response['push_type'] = list(push_type.values())
        response['general'] = list(general_type.values())
        return JsonResponse(response, safe=False)


    response['deeplink'] = deeplink_type
    response['push_type'] = push_type
    response['general'] = general_type
    return render(request, 'qa_tools/braze_notification/notificationDetail.html', context={"project_name": project,
                                                                        "response": response,
                                                                                           })


def send_braze_push(request):
    if request.method == 'POST':
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
    if request.method == 'POST':
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
                response['data'] = {
                    'nid': res.nid,
                    'project_id': res.project_id,
                    'push_type': res.push_type,
                    'content': res.content
                }
            else:
                response['msg'] = 'Add push failed, please try again.'

        return JsonResponse(response)


def sdk_config(request):
    if request.method == 'GET':
        sdk_configs = models.SdkConifg.objects.all()

        data_format = request.GET.get('format')
        if data_format == 'json':
            sdk_configs = list(sdk_configs.values())
            return JsonResponse(sdk_configs, safe=False)

        return render(request, template_name='qa_tools/sdk_parse/sdk_config_list.html', context={'app_keys': sdk_configs})


def sdk_config_detail(request, appkey):
    if request.method == 'GET':
        data_format = request.GET.get('format')

        sdk_config = SdkConfigParse()
        try:
            sdk_config.parse(appkey)
        except Exception as erro_msg:
            if data_format == 'json':
                response = {
                    'code': 'failed',
                    'msg': str(erro_msg)
                }
                return JsonResponse(response, safe=False)

            return render(request, template_name='qa_tools/sdk_parse/sdk_config_error.html',
                          context={'error_msg': erro_msg})

        else:
            if data_format == 'json':
                data = {'configurl': sdk_config.configurl,
                        'configjson': sdk_config.text_decrypted_trim,
                        'support': sdk_config.issupported,
                       'comments': sdk_config.comments}
                response = {
                    'code': 'success',
                    'msg': data
                }
                return JsonResponse(response, safe=False)

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
                response['data'] = {
                    'nid': res.nid,
                    'project_name': res.project_name,
                    'config_type': res.config_type,
                    'app_key': res.app_key
                }
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


# not verify csrf.
@require_POST
@method_decorator(csrf_exempt, name='dispatch')
def android_upload_api(request):
    if request.method == 'POST':
        date = request.body.decode('utf-8')

        # deserialize string to python list object
        date_list = json.loads(date)
        for data_dict in date_list:
            project_name = data_dict['packageName']
            project = project_info_models.AndroidProject.objects.filter(project_name=project_name).first()
            # check project table is whether create this project.
            if not project:
                project = project_info_models.AndroidProject.objects.create(project_name=project_name)
            else:
                # refresh this project update date.
                project.save()

            # check current build info is whether exists.
            # rules: package_name, package_version_name,
            # product_flavor_name, module_name combination only have one record.
            build_record = project_info_models.AndroidBuild.objects.filter(package_name=data_dict['package'],
                                                              package_version_name=data_dict['packageVersionName'],
                                                              product_flavor_name=data_dict['productFlavorName'],
                                                              module_name=data_dict['moduleName']).first()

            snapshot = False
            library_coordinate_list = data_dict['libraryCoordinateList']
            # check is whether exist snapshot library.
            for library_dict in library_coordinate_list:
                if '-SNAPSHOT' in library_dict['currentVersion']:
                    snapshot = True
                    break

            # serialize library_coordinate_list to string to save database.
            library_coordinate_string = json.dumps(library_coordinate_list)
            # check this build record is whether exist, if not exist create,
            package_mapping_url = '/media/android_mapping/'
            if data_dict['moduleName']:
                package_mapping_url = package_mapping_url + data_dict['moduleName'] + \
                                      '_' + data_dict['package'] + '_' + data_dict['packageVersionName'] + \
                                      '_mapping.text'
            else:
                package_mapping_url = package_mapping_url + data_dict['package'] + '_' + \
                                      data_dict['packageVersionName'] + '_mapping.text'
            if not build_record:
                project_info_models.AndroidBuild.objects.create(project=project,
                                                     package_name=data_dict['package'],
                                                     package_version_name=data_dict['packageVersionName'],
                                                     package_version_code=data_dict['packageVersionCode'],
                                                     module_name=data_dict['moduleName'],
                                                     product_flavor_name=data_dict['productFlavorName'],
                                                     package_target_sdk=int(data_dict['packageTargetSdk']),
                                                     package_mini_sdk=int(data_dict['packageMiniSdk']),
                                                     package_mapping_url=package_mapping_url,
                                                     deeplink_scheme=data_dict['deepLinkScheme'],
                                                     git_sha_code=data_dict['gitSHACode'],
                                                     git_branch_name=data_dict['gitBranchName'],
                                                     snapshot=snapshot,
                                                     library_coordinate_list=library_coordinate_string)
            else:
                # to support update last modify, use .save to update data, not use .update()
                build_record.project=project
                build_record.package_name=data_dict['package']
                build_record.package_version_name=data_dict['packageVersionName']
                build_record.package_version_code=data_dict['packageVersionCode']
                build_record.module_name=data_dict['moduleName']
                build_record.product_flavor_name=data_dict['productFlavorName']
                build_record.package_target_sdk=int(data_dict['packageTargetSdk'])
                build_record.package_mini_sdk=int(data_dict['packageMiniSdk'])
                build_record.package_mapping_url=package_mapping_url
                build_record.deeplink_scheme=data_dict['deepLinkScheme']
                build_record.git_sha_code=data_dict['gitSHACode']
                build_record.git_branch_name=data_dict['gitBranchName']
                build_record.snapshot=snapshot
                build_record.library_coordinate_list=library_coordinate_string
                build_record.save()

        return HttpResponse('Project info stored')


@require_POST
@method_decorator(csrf_exempt, name='dispatch')
def ios_upload_api(request):
    if request.method == 'POST':
        date = request.body.decode('utf-8')
        # deserialize string to python list object
        date_list = json.loads(date)
        for data_dict in date_list:
            project_name = data_dict['projectName']
            project = project_info_models.IosProject.objects.filter(project_name=project_name).first()
            # check project table is whether create this project.
            if not project:
                project = project_info_models.IosProject.objects.create(project_name=project_name)
            else:
                # refresh project update date.
                project.save()

            # check current build info is whether exists.
            # rules: project and project_version combination only have one record.

            build_record = project_info_models.IosBuild.objects.filter(project=project,
                                                          project_version=data_dict['projectVersion']).first()
            x_framework = False
            frameworks_list = data_dict['frameworks']
            # check is whether exist snapshot library.
            for framework_dict in frameworks_list:
                if re.match(r'\d+\.\d+\.0\d+', framework_dict['frameworkVersion']) \
                        or 'x' in str(framework_dict['frameworkVersion']):
                    x_framework = True
                    break

            # serialize frameworks_list to string to save database.
            frameworks_string = json.dumps(frameworks_list)
            # check this build record is whether exist, if not exist create,
            if not build_record:
                project_info_models.IosBuild.objects.create(project=project,
                                               project_version=data_dict['projectVersion'],
                                               x_framework=x_framework,
                                               framework=frameworks_string)
            else:
                build_record.project = project
                build_record.project_version = data_dict['projectVersion']
                build_record.x_framework = x_framework
                build_record.framework = frameworks_string
                build_record.save()

        return HttpResponse('Project info stored')


@require_POST
@method_decorator(csrf_exempt, name='dispatch')
def android_mapping_upload_api(request):
    if 'file' not in request.FILES:
        return HttpResponse('No such file')
    else:
        file = request.FILES.get('file')
        upload_dir = os.path.join(MEDIA_ROOT, 'android_mapping')
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
        upload_path = os.path.join(upload_dir, secure_filename(file.name))
        with open(upload_path, 'wb') as f:
            for line in file:
                f.write(line)
        return HttpResponse('Upload file success')


def localization_tool(request):

    return render(request, 'qa_tools/localization_tool/localization_tool.html')


def localization_upload(request):
    response = {'code': 'success', 'msg': '', 'filename': ''}
    file = request.FILES.get('file')
    if file is None:
        response['code'] = 'fail'
        response['msg'] = 'Please select a localization file.'
    else:
        file_name = file.name
        if not file_name.endswith('.string'):
            response['code'] = 'fail'
            response['msg'] = 'File format is incorrect, Please upload .string file.'
        else:
            upload_dir = os.path.join(MEDIA_ROOT, 'localization_file')
            if not os.path.exists(upload_dir):
                os.mkdir(upload_dir)
            else:
                file_list = os.listdir(upload_dir)
                for item in file_list:
                    os.remove(os.path.join(upload_dir, item))
            file_path = os.path.join(upload_dir, file_name)
            with open(file_path, 'wb') as f:
                for line in file:
                    f.write(line)
            file_modify_name = file_name.split('.')[0] + '_modify.string'
            file_modify_path = os.path.join(upload_dir, file_modify_name)
            try:
                localization_value2number(file_path, file_modify_path)
            except Exception:
                response['code'] = 'fail'
                response['msg'] = 'Format file error, please reupload.'
            else:
                response['msg'] = 'Upload success, please download.'
                response['filename'] = file_modify_name
    return JsonResponse(response)

def get_csrf_token(request):
    return get_token(request)











