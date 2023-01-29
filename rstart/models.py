from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from datetime import date

# model for recruiter profiles
class Recruiter(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    zipcode = models.IntegerField(default=00000)
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.username

class JobPosting(models.Model):
    recruiter = models.CharField(max_length=200)
    company = models.CharField(max_length=200)

    candidate = models.CharField(max_length=200, null=True)
    interested = models.IntegerField(default=0)

    position = models.CharField(max_length=200)
    postype = models.BooleanField()
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    skills = models.CharField(max_length=200)
    expiration = models.DateField()
    status = models.BooleanField()

    def is_expired(self):
        return not (date.today() < self.expiration)

    def num_interested(self):
        return len(JobInteraction.objects.filter(job=self.id, interested=True))

class JobInteraction(models.Model):
    candidate = models.IntegerField()
    job = models.IntegerField()
    interested = models.BooleanField()

class JobOffer(models.Model):
    candidate = models.IntegerField()
    job = models.IntegerField()
    accepted = models.BooleanField(default=False)