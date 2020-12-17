from django.db import models

# Create your models here.

# projects table
class Project(models.Model):
    nid = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Project Name', max_length=32)
    scheme = models.CharField(verbose_name='Prefix Name', max_length=64)
    
    def __str__(self):
        return self.name


# deeplink detail table
class Contents(models.Model):
    nid = models.AutoField(primary_key=True)
    body = models.CharField(verbose_name='Deeplink Detail', max_length=128)
    create_time = models.DateTimeField(verbose_name='Create Time', auto_now_add=True)
    classification = models.CharField(verbose_name="Classification", null=True, max_length=32)
    # foreign key to Project nid
    project = models.ForeignKey(verbose_name='Project Name', to='Project', to_field='nid', default=None, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.body



