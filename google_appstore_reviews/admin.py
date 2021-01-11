from django.contrib import admin

from .models import ReviewInfo, ReviewDetail
# Register your models here.

@admin.register(ReviewInfo)
class ReviewInfoAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'author', 'platform', 'country']


@admin.register(ReviewDetail)
class ReviewDetailAdmin(admin.ModelAdmin):
    list_display = ['nid', 'title', 'rating', 'create_time']

