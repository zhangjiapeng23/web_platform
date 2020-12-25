from django.db import models

# Create your models here.

class Project(models.Model):
    nid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name='Project Name')
    scheme = models.CharField(max_length=40, verbose_name='Project Scheme')
    api_key = models.CharField(max_length=128, verbose_name='API Key')
    instance_url = models.CharField(max_length=128, verbose_name='Notification Server Url')

    def __str__(self):
        return self.name

class Notification(models.Model):
    TYPE_OPTIONS = (
        (0, 'PUSH_TYPE'),
        (1, 'deeplink'),
        (2, 'general')
    )
    nid = models.AutoField(primary_key=True)
    type = models.IntegerField(choices=TYPE_OPTIONS, verbose_name='Notification Type')
    content = models.CharField(max_length=128, verbose_name='Notification Content')

    project = models.ForeignKey(to='Project', to_field='nid', verbose_name='Project Name', on_delete=models.CASCADE)


    def __str__(self):
        return self.TYPE_OPTIONS[self.type][1] + ':' + self.content



