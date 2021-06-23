from django.db import models

# Create your models here.


class Project(models.Model):
    nid = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    android_id = models.CharField(max_length=128, null=True, blank=True)
    ios_id = models.CharField(max_length=128, null=True, blank=True)
    support_region = models.IntegerField()
    project_logo = models.FileField(upload_to='imgs/app_review_project',
                                    default='imgs/app_review_project/Neulion.png')
    android_origin = models.CharField(max_length=256, null=True, blank=True)
    ios_origin = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.project_name


class ReviewInfo(models.Model):
    PLATFORM_OPTIONS = (
        (0, 'Android'),
        (1, 'iOS')
    )
    nid = models.AutoField(primary_key=True)
    review_id = models.CharField(max_length=128, unique=True)
    author = models.CharField(max_length=256)
    platform = models.IntegerField(choices=PLATFORM_OPTIONS)
    country = models.CharField(max_length=36)
    project_name = models.ForeignKey(to_field='project_name',
                                     to='Project',
                                     on_delete=models.CASCADE)

    def __str__(self):
        return self.country + '_' + self.author


class ReviewDetail(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, null=True)
    content = models.TextField(null=True)
    rating = models.IntegerField(null=True)
    version = models.CharField(max_length=12, null=True)
    create_time = models.DateTimeField(auto_created=True)
    review_info = models.OneToOneField(to='ReviewInfo', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        text = "{}, Rating: {}, Version: {}, Comment Date: {}"
        return text.format(self.title, self.rating, self.version, self.create_time)
