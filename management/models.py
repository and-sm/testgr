from django.db import models


class Settings(models.Model):
    running_jobs_age = models.IntegerField(blank=True, null=True)
