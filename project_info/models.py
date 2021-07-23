from django.db import models

# Create your models here.


class AndroidProject(models.Model):
    nid = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=128, unique=True)
    project_logo = models.FileField(upload_to='imgs/project_info', default='imgs/project_info/Neulion.png')
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name


class IosProject(models.Model):
    nid = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=128, unique=True)
    project_logo = models.FileField(upload_to='imgs/project_info', default='imgs/project_info/Neulion.png')
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name


class AndroidBuild(models.Model):
    nid = models.AutoField(primary_key=True)
    project = models.ForeignKey(to='AndroidProject', to_field='project_name',
                                on_delete=models.CASCADE)
    package_name = models.CharField(max_length=128)
    package_version_name = models.CharField(max_length=128)
    package_version_code = models.IntegerField()
    module_name = models.CharField(max_length=128)
    product_flavor_name = models.CharField(max_length=128)
    package_target_sdk = models.IntegerField(null=True)
    package_mini_sdk = models.IntegerField(null=True)
    package_mapping_url = models.CharField(max_length=256, null=True)
    deeplink_scheme = models.CharField(max_length=128, null=True)
    git_sha_code = models.CharField(max_length=128, null=True)
    git_branch_name = models.CharField(max_length=128, null=True)
    date = models.DateTimeField(auto_now=True)
    snapshot = models.BooleanField()
    library_coordinate_list = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['package_name',
                                            'package_version_name',
                                            'product_flavor_name',
                                            'module_name'], name='%(class)s_unique_build')]


class IosBuild(models.Model):
    nid = models.AutoField(primary_key=True)
    project = models.ForeignKey(to='IosProject', to_field='project_name', on_delete=models.CASCADE)
    project_version = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now=True)
    x_framework = models.BooleanField()
    framework = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'project_version'], name='%(class)s_unique_build')
        ]




