from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# model for candidate profiles
class Candidate(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(max_length=500, blank=True, default='')
    zipcode = models.IntegerField(default=00000)
    skills = models.CharField(max_length=200)
    github = models.CharField(max_length=200, blank=True, default='')
    years = models.IntegerField(default=0)
    education = models.CharField(max_length=300, blank=True, default='')
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.username
