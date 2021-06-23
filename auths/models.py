from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserInfo(AbstractUser):

    nid = models.AutoField(primary_key=True)
    logo = models.FileField(upload_to='imgs/user_logo',
                            default='imgs/user_logo/account_default.png')