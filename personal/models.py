from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255,null=True)
    user_last = models.CharField(max_length=255,null=True)
    user_school = models.CharField(max_length=255,null=True)
    user_phone = models.IntegerField(max_length=10,null=True)
    user_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username