from django.db import models
from django.contrib.auth.models import User

class profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=False)
    authentication_code=models.CharField(max_length=200, default='', blank=True)
    date_on_birth=models.DateField(blank=True,null=True)


