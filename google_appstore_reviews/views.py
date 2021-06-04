import time
from functools import reduce

from django.shortcuts import render
from django.db.models import Avg, F
from django.http.response import JsonResponse

from google_appstore_reviews import models
from mobile_QA_web_platform import settings
from google_appstore_reviews.crawler_tools.register_crawler import registered
from google_appstore_reviews.crawler_tools.run_crawler import crawler_start

# Create your views here.


def reviews_project_index(request, project):
    for project_registed in registered:
         if project_registed.project_name == project:
             app_id = project_registed.ios_id
             android_id = project_registed.android_id
             country = project_registed.countries[0].code
             break

    return render(request, 'google_appstore_reviews/reviews_project_index.html', context={'project': project,
                                                                                          'app_id': app_id,
                                                                                          'android_id': android_id,
                                                                                          'country': country})


def reviews_projects_list(request):
    # method post to create a project
    if request.method == 'POST':
        response = {
            'code': 'failed',
            'message': "Project create failed.",
            'data': {
                'project_name': '',
                'android_id': '',
                'ios_id': '',
                'support_region': ''
            }
        }
        project_name = request.POST.get('project_name')
        android_id = request.POST.get('android_id')
        ios_id = request.POST.get('ios_id')
        support_region = request.POST.get('support_region')
        project_logo = request.FILES.get('project_logo')
        if not project_name:
            response['data']['project_name'] = 'Project name is required.'
        # if not android_id:
        #     response['data']['android_id'] = 'Android id is required.'
        # if not ios_id:
        #     response['data']['ios_id'] = 'iOS id is required.'
        if not support_region:
            response['data']['support_region'] = 'Support region is required.'
        else:
            # check project name is whether unique
            origin_name = project_name
            project_name = origin_name.replace(' ', '_')
            project_res = models.Project.objects.filter(project_name=project_name).first()
            if project_res:
                response['data']['project_name'] = f'Project name: {origin_name} is used.'
            else:
                support_region = reduce(lambda x,y: int(x)+int(y), support_region.split(','))
                android_origin = f'https://play.google.com/store/apps/details?id={android_id}&showAllReviews=true'
                ios_origin = f'https://itunes.apple.com/rss/customerreviews/page=1/id={ios_id}/sortby=mostrecent/json'
                if project_logo:
                    models.Project.objects.create(project_name=project_name,
                                                  android_id=android_id,
                                                  ios_id=ios_id,
                                                  support_region=support_region,
                                                  project_logo=project_logo,
                                                  android_origin=android_origin,
                                                  ios_origin=ios_origin)
                else:
                    models.Project.objects.create(project_name=project_name,
                                                  android_id=android_id,
                                                  ios_id=ios_id,
                                                  support_region=support_region,
                                                  android_origin=android_origin,
                                                  ios_origin=ios_origin)

                response['code'] = 'success'
                response['message'] = f'Project {project_name} create success.'
                # run crawler to get review data for new project
                crawler_start(model='once')

        return JsonResponse(response, safe=False)

    # method get to get project list
    if request.method == 'GET':
        data_format = request.GET.get('format')
        if data_format == 'json':
            host = settings.LOCAL_HOST
            port = settings.LOCAL_PORT
            media_path = settings.MEDIA_URL
            projects_obj = models.Project.objects.all().values()
            projects_list = list(projects_obj)
            for item in projects_list:
                item['project_logo'] = f'{host}:{port}{media_path}{item["project_logo"]}'
            return JsonResponse(projects_list, safe=False)

    return render(request, 'google_appstore_reviews/reviews_projects_list.html')


def reviews_project_detail_api(request, project, platform):
    if request.method == 'GET':
        data_format = request.GET.get('format')
        if data_format == 'json':
            platform = 0 if platform.lower() == 'android' else 1
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('pageSize', 10))
            rating_filter = request.GET.get('rating')
            region_filter = request.GET.get('region')
            version_filter = request.GET.get('version')

            # get request basic data obj
            basic_data_obj = models.ReviewDetail.objects.filter(review_info__project_name=project,
                                                                review_info__platform=platform).\
                                                                exclude(version__regex=r"^[0-9]{1}\.[0-9]{1}$").\
                                                                exclude(version__regex=r"[0-9]*\.[0-9]*\.[0-9]*")

            # get version list
            version_filter_list = basic_data_obj.all().values_list('version').distinct()
            version_filter_list = [i[0] for i in version_filter_list if i[0] is not None and len(i[0].split('.')) == 2]
            version_filter_list.sort(key=lambda x: float(x), reverse=True)

            # get rating list
            rating_filter_list = [i[0] for i in basic_data_obj.all().values_list('rating').distinct()]
            rating_filter_list.sort(reverse=True)

            # get region list

            # NBA special logic: two version
            region_filter_list = list()
            if project == 'NBA':
                domestic_count = basic_data_obj.all().filter(review_info__country='us').count()
                international_count = basic_data_obj.all().exclude(review_info__country='us').count()

                if domestic_count:
                    region_filter_list.append('Domestic')
                if international_count:
                    region_filter_list.append('International')
            else:
                country = basic_data_obj.values_list("review_info__country").first()[0]
                region_filter_list.append(country)

            filter_list = dict()
            filter_list['rating'] = rating_filter_list
            filter_list['region'] = region_filter_list
            filter_list['version'] = version_filter_list

            # get this request basic data obj by filter
            if rating_filter:
                basic_data_obj = basic_data_obj.filter(rating=rating_filter)

            if region_filter:
                if region_filter == 'Domestic':
                    basic_data_obj = basic_data_obj.filter(review_info__country='us')
                elif region_filter == 'International':
                    basic_data_obj = basic_data_obj.exclude(review_info__country='us')
                else:
                    basic_data_obj = basic_data_obj.filter(review_info__country=region_filter)

            if version_filter:
                basic_data_obj = basic_data_obj.filter(version=version_filter)

            # paging data
            total = basic_data_obj.count()
            paging_data_obj = basic_data_obj.order_by('-create_time').all()[(page - 1) * page_size:page * page_size]
            total_pages = total // page_size + 1 if total % page_size else total // page_size

            # get review summary info dict
            review_summary = dict()
            if total:
                rating_avg = basic_data_obj.all().aggregate(Avg('rating'))
                rating_kind_num = [basic_data_obj.filter(rating=i).count() / total for i in range(1, 6)]
                rating_kind_percent = ['%.2f%%' % (num * 100) for num in rating_kind_num]
                review_summary['rating_avg'] = '%.1f' % rating_avg['rating__avg']
                review_summary['rating_kind_percent'] = rating_kind_percent
                review_summary['rating_total'] = total
            else:
                review_summary['rating_avg'] = '0.0'
                review_summary['rating_kind_percent'] = ["0.00%", "0.00%", "0.00%", "0.00%", "0.00%"]
                review_summary['rating_total'] = 0

            data_list = list(paging_data_obj.values("nid",
                                                    "title",
                                                    "content",
                                                    "rating",
                                                    "version",
                                                    "create_time",
                                                    author=F("review_info__author"),
                                                    region=F("review_info__country")))
            response = {
                'page': page,
                'pageSize': page_size,
                'totalPages': total_pages,
                'filterList': filter_list,
                'reviewSummary': review_summary,
                'data': data_list
            }
            return JsonResponse(response, safe=False)


def reviews_project_detail(request, project):
    platform = request.GET.get('platform', 'android')
    platform = 0 if platform.lower() == 'android' else 1
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 10))
    filter_select_list = request.GET.get('filter', '* * *').split()

    # get this request basic data obj
    basic_data_obj = models.ReviewDetail.objects.filter(review_info__project_name=project,
                                                        review_info__platform=platform).\
                                                        exclude(version__regex=r"^[0-9]{1}\.[0-9]{1}$").\
                                                        exclude(version__regex=r"[0-9]*\.[0-9]*\.[0-9]*")

    # get version list
    version_filter = basic_data_obj.all().values_list('version').distinct()
    version_filter = [i[0] for i in version_filter if i[0] is not None and len(i[0].split('.')) == 2]
    version_filter.sort(key=lambda x: float(x), reverse=True)

    # get rating list
    rating_filter = [i[0] for i in basic_data_obj.all().values_list('rating').distinct()]
    rating_filter.sort(reverse=True)

    # get region list

    # NBA special logic: two version
    region_filter = list()
    if project == 'NBA':
        domestic_count = basic_data_obj.all().filter(review_info__country='us').count()
        international_count = basic_data_obj.all().exclude(review_info__country='us').count()

        if domestic_count:
            region_filter.append('Domestic')
        if international_count:
            region_filter.append('International')
    else:
        country = basic_data_obj.values_list("review_info__country").first()[0]
        region_filter.append(country)

    filter_list = dict()
    filter_list['rating'] = rating_filter
    filter_list['region'] = region_filter
    filter_list['version'] = version_filter

    # get this request basic data obj by filter
    if filter_select_list[0] != '*':
        basic_data_obj = basic_data_obj.filter(rating=filter_select_list[0])

    if filter_select_list[1] != '*':
        if filter_select_list[1] == 'Domestic':
            basic_data_obj = basic_data_obj.filter(review_info__country='us')
        elif filter_select_list[1] == 'International':
            basic_data_obj = basic_data_obj.exclude(review_info__country='us')
        else:
            basic_data_obj = basic_data_obj.filter(review_info__country=filter_select_list[1])

    if filter_select_list[2] != '*':
        basic_data_obj = basic_data_obj.filter(version=filter_select_list[2])

    # get page index information
    total = basic_data_obj.count()
    review_obj = basic_data_obj.order_by('-create_time').all()[(page - 1) * page_size:page * page_size]
    total_pages = total // page_size + 1 if total % page_size else total // page_size
    start_page = page - 2 if page - 2 > 1 else 1
    end_page = start_page + 4 if start_page + 4 < total_pages else total_pages
    page_index = [index for index in range(start_page, end_page + 1)]

    # get review summary info dict
    review_summary = dict()
    if total:
        rating_avg = basic_data_obj.all().aggregate(Avg('rating'))
        rating_kind_num = [basic_data_obj.filter(rating=i).count() / total for i in range(1, 6)]
        rating_kind_percent = ['%.2f%%' % (num * 100) for num in rating_kind_num]
        review_summary['rating_avg'] = '%.1f' % rating_avg['rating__avg']
        review_summary['rating_king_percent'] = rating_kind_percent
        review_summary['rating_total'] = total
    else:
        review_summary['rating_avg'] = '0.0'
        review_summary['rating_king_percent'] = []
        review_summary['rating_total'] = 0

    return render(request, 'google_appstore_reviews/reviews_project_detail.html', context={'project': project,
                                                                                       'reviews': list(review_obj),
                                                                                       'filter_select_list':
                                                                                           filter_select_list,
                                                                                       'filter_list': filter_list,
                                                                                       'page_index': page_index,
                                                                                       'total_pages': total_pages,
                                                                                       'review_summary': review_summary,
                                                                                           })
