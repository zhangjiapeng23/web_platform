from django.db import models


# Create your models here.
from django.db.models.functions import datetime


class Project(models.Model):

    nid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    logo = models.FileField(upload_to='imgs/testcase',
                            default='imgs/testcase/Neulion.png')

    def __str__(self):
        return self.name


class Testcase(models.Model):

    class Classification(models.TextChoices):
        WEB = 'web', 'WEB'
        IOS = 'iOS', 'IOS'
        ANDROID = 'Android', 'ANDROID'
        API = 'Api', 'API'

    class Meta:
        ordering = ['-last_modified']

    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, default="testcase name")
    node_id = models.CharField(max_length=128, unique=True)
    description = models.TextField(default="testcase description")
    project = models.ForeignKey(to_field='nid',
                                to='Project',
                                on_delete=models.CASCADE)
    classification = models.CharField(max_length=12,
                                      choices=Classification.choices,
                                      default=Classification.WEB)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<%s %s>" % (self.classification, self.node_id)


class TestTask(models.Model):

    nid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    job_name = models.CharField(max_length=128)
    testcase = models.ManyToManyField(to='Testcase')
    project = models.ForeignKey(to_field='nid',
                                to='Project',
                                on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(to_field='nid',
                              to='auths.UserInfo',
                              on_delete=models.CASCADE)
    last_execute = models.DateTimeField(null=True, blank=True)
    execute_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def execute(self):
        self.execute_count += 1
        self.last_execute = datetime.datetime.now()
        self.save()

    class Meta:
        ordering = ['-last_modified']


class TaskExecuteRecord(models.Model):

    class Status(models.TextChoices):
        cancel = 'Cancel', 'CANCEL'
        running = 'Running', 'RUNNING'
        finish = 'Finish', 'FINISH'

    nid = models.AutoField(primary_key=True)
    task = models.ForeignKey(to_field='name', to='TestTask', on_delete=models.CASCADE)
    job_name = models.CharField(max_length=128)
    build_id = models.IntegerField()
    build_url = models.CharField(max_length=256)
    status = models.CharField(max_length=12,
                              choices=Status.choices,
                              default=Status.running)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    report = models.OneToOneField(to_field='nid',
                                  to='Report',
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE)

    def __str__(self):
        return self.build_url

    class Meta:
        ordering = ['-start_time']


class Report(models.Model):

    nid = models.AutoField(primary_key=True)
    report = models.FileField(upload_to='report')
    testcase_total = models.IntegerField()
    pass_total = models.IntegerField()
    failed_total = models.IntegerField()
    ignore_total = models.IntegerField()
    task = models.ForeignKey(to_field='nid', to='TestTask', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.task, self.create_time)







