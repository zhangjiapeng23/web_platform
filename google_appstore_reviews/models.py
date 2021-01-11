from django.db import models

# Create your models here.

class ReviewInfo(models.Model):
    PLATFORM_OPTIONS = (
        (0, 'Android'),
        (1, 'iOS')
    )
    nid = models.AutoField(primary_key=True)
    review_id = models.CharField(max_length=128, unique=True)
    author = models.CharField(max_length=36)
    platform = models.IntegerField(choices=PLATFORM_OPTIONS)
    country = models.CharField(max_length=36)

    def __str__(self):
        return self.country + '_' + self.author

class ReviewDetail(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    content = models.TextField()
    rating = models.IntegerField()
    version = models.CharField(max_length=12)
    create_time = models.DateTimeField(auto_created=True)
    review_info = models.OneToOneField(to='ReviewInfo', to_field='nid', on_delete=models.CASCADE)


    def __str__(self):
        text = "{}, Rating: {}, Version: {}, Comment Date: {}"
        return text.format(self.title, self.rating, self.version, self.create_time)
