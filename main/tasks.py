from testgr.celery import app
from loader.models import TestJobs
from management.models import Settings
from datetime import timedelta
from django.utils import timezone


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Stop running jobs every 5 minutes if job age > running_jobs_max_age_minutes
    sender.add_periodic_task(10, task_stop_running_jobs.s(), name='Clean running jobs')


@app.task()
def task_stop_running_jobs():
    settings = Settings.objects.get(pk=1)
    if settings.running_jobs_age == 0 or settings.running_jobs_age is None:
        pass
    else:
        running_jobs = TestJobs.objects.filter(status=1)
        for job in running_jobs:
            if job.start_time + timedelta(minutes=settings.running_jobs_age) < timezone.now():
                job.status = 4
                job.save()
