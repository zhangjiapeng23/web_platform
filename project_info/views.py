import json
import re

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from . import models


# Create your views here.

def index(request):
    return HttpResponse('it is index page!')


def android_project_list(request):
    return HttpResponse('it is android project list')


def android_project_detail(request, project):
    return HttpResponse('it is android {} project detail'.format(project))


def android_library_detail(request):
    return HttpResponse('it is android library detail')


def ios_project_list(request):
    return HttpResponse('it is iOS project list')


def ios_project_detail(request, project):
    return HttpResponse('it is iOS {} project detail'.format(project))


def ios_library_detail(request):
    return HttpResponse('it is iOS library detail')


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
            project = models.AndroidProject.objects.filter(project_name=project_name).first()
            # check project table is whether create this project.
            if not project:
                project = models.AndroidProject.objects.create(project_name=project_name)

            # check current build info is whether exists.
            # rules: package_name, package_version_name,
            # product_flavor_name, module_name combination only have one record.
            build_record = models.AndroidBuild.objects.filter(package_name=data_dict['package'],
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
            if not build_record:
                models.AndroidBuild.objects.create(project=project,
                                                     package_name=data_dict['package'],
                                                     package_version_name=data_dict['packageVersionName'],
                                                     module_name=data_dict['moduleName'],
                                                     product_flavor_name=data_dict['productFlavorName'],
                                                     packaget_target_sdk=int(data_dict['packageTargetSdk']),
                                                     packaget_mini_sdk=int(data_dict['packageMiniSdk']),
                                                     package_mapping_url=data_dict['packageMappingUrl'],
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
                build_record.module_name=data_dict['moduleName']
                build_record.product_flavor_name=data_dict['productFlavorName']
                build_record.packaget_target_sdk=int(data_dict['packageTargetSdk'])
                build_record.packaget_mini_sdk=int(data_dict['packageMiniSdk'])
                build_record.package_mapping_url=data_dict['packageMappingUrl']
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
            project = models.IosProject.objects.filter(project_name=project_name).first()
            # check project table is whether create this project.
            if not project:
                project = models.IosProject.objects.create(project_name=project_name)

            # check current build info is whether exists.
            # rules: project and project_version combination only have one record.

            build_record = models.IosBuild.objects.filter(project=project,
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
                models.IosBuild.objects.create(project=project,
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
