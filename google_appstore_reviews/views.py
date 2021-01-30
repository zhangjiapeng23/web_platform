from django.shortcuts import render
from django.db.models import Avg, Sum, Count

from google_appstore_reviews import models


# Create your views here.


def reviews_project_index(request, project):
    return render(request, 'google_appstore_reviews/reviews_project_index.html', context={'project': project})


def reviews_projects_list(request):
    return render(request, 'google_appstore_reviews/reviews_projects_list.html')


def reviews_project_detail(request, project):
    platform = request.GET.get('platform', 'android')
    platform = 0 if platform.lower() == 'android' else 1
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 10))
    filter_select_list = request.GET.get('filter', '* * *').split()

    # get this request basic data obj
    basic_data_obj = models.ReviewDetail.objects.filter(review_info__project_name=project,
                                                        review_info__platform=platform)

    # get version list
    version_filter = basic_data_obj.all().values_list('version').distinct()
    version_filter = [i[0] for i in version_filter if i[0] is not None and 1 < len(i[0].split('.')) < 3]
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
    total_pages = total // page_size + 1 if total % 10 else total // page_size
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
