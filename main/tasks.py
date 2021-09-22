from testgr.celery import app
from loader.models import TestJobs
from management.models import Settings
from datetime import timedelta
from django.utils import timezone
from loader.redis import Redis


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Will stop running jobs every 5 minutes if job age > running_jobs_max_age_minutes
    sender.add_periodic_task(300, task_stop_running_jobs.s(), name='Clean running jobs')


@app.task()
def task_stop_running_jobs():
    redis = Redis()
    settings = Settings.objects.filter(pk=1).first()
    if settings:
        if settings.running_jobs_age == 0 or settings.running_jobs_age is None:
            pass
        else:
            running_jobs = TestJobs.objects.filter(status=1)
            for job in running_jobs:
                if job.start_time + timedelta(minutes=settings.running_jobs_age) < timezone.now():
                    job.status = 4
                    job.save()
                    if job.custom_id:
                        job_to_delete = "job_" + job.custom_id
                        redis.connect.lrem("running_jobs", 0, job_to_delete)
                        redis.connect.delete("job_" + job.custom_id)
                    else:
                        job_to_delete = "job_" + job.uuid
                        redis.connect.lrem("running_jobs", 0, job_to_delete)
                        redis.connect.delete("job_" + job.uuid)
