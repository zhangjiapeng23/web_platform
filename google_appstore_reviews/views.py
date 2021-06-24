from django.shortcuts import render
from django.db.models import Avg, F
from django.http.response import JsonResponse

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions

from .forms import ProjectForm
from google_appstore_reviews import models
from mobile_QA_web_platform.settings import base
from google_appstore_reviews.crawler_tools.register_crawler import registered
from google_appstore_reviews.crawler_tools.run_crawler import crawler_start
from .serializers import ProjectListSerializer, ProjectSerializer, \
    ReviewInfoListSerializer, ReviewDetailListSerializer
from .utils.pagination import StandardResultsSetPagination
from .utils.review_filter import ReviewFilter


# Create your views here.

class ProjectList(generics.ListCreateAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class Project(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ReviewInfoList(generics.ListAPIView):

    queryset = models.ReviewInfo.objects.all()
    serializer_class = ReviewInfoListSerializer
    pagination_class = StandardResultsSetPagination


class ReviewDetailList(generics.ListAPIView):

    queryset = models.ReviewDetail.objects.all()
    serializer_class = ReviewDetailListSerializer
    pagination_class = StandardResultsSetPagination
    filter_class = ReviewFilter


class ReviewDetailProjectList(generics.ListAPIView):

    serializer_class = ReviewDetailListSerializer
    pagination_class = StandardResultsSetPagination
    filter_class = ReviewFilter

    def get_queryset(self):
        """
        This view should return a list of corresponding project.
        :return:
        """
        project = self.kwargs['project_name']
        return models.ReviewDetail.objects.filter(review_info__project_name=project)


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


class ReviewsProjectList(APIView):
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        data_format = request.GET.get('format')
        if data_format == 'json':
            host = base.LOCAL_HOST
            port = base.LOCAL_PORT
            media_path = base.MEDIA_URL
            projects_obj = models.Project.objects.all().values()
            projects_list = list(projects_obj)
            for item in projects_list:
                item['project_logo'] = f'{host}:{port}{media_path}{item["project_logo"]}'
            return JsonResponse(projects_list, safe=False)

        return render(request, 'google_appstore_reviews/reviews_projects_list.html')

    def post(self, request):
        create_response = {
            'code': 'failed',
            'message': "Project create failed.",
            'data': {}
        }
        form = ProjectForm(request.POST, request.FILES)
        if not form.is_valid():
            create_response['data'] = form.errors
        else:
            project_name = form.cleaned_data.get('project_name')
            android_id = form.cleaned_data.get('android_id')
            ios_id = form.cleaned_data.get('ios_id')
            support_region = form.cleaned_data.get('support_region')
            project_logo = form.cleaned_data.get('project_logo')
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
            create_response['code'] = 'success'
            create_response['message'] = f'Project {project_name} create success.'
            # run crawler to get review data for new project
            crawler_start(model='once')

        return JsonResponse(create_response, safe=False)


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
                country_list = basic_data_obj.values_list("review_info__country").first()
                region_filter_list = country_list if country_list else []

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
            # make sure total_pages greater than 0
            total_pages = total_pages if total_pages > 0 else 1

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
