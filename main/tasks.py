from testgr.celery import app
from loader.models import TestJobs, Tests
from management.models import Settings
from datetime import timedelta
from django.utils import timezone
from loader.redis import Redis
from tools.tools import unix_time_to_datetime
from datetime import datetime
from datetime import timezone as timezone_native

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

                    # Job
                    job.status = 4
                    job.stop_time = unix_time_to_datetime(
                        int(datetime.now(tz=timezone_native.utc).timestamp() * 1000))
                    job.time_taken = job.stop_time - job.start_time

                    # Tests
                    aborted_tests = 0
                    if job.tests_in_progress is not None and job.tests_in_progress > 0:
                        result = Tests.objects.filter(job=job, status=2)
                        for test_item in result:
                            test_item.status = 6
                            aborted_tests += 1
                            if job.tests_in_progress is not None and job.tests_in_progress > 0:
                                job.tests_in_progress = job.tests_in_progress - 1
                            test_item.save()
                    job.tests_aborted = aborted_tests

                    job.save()

                    # Redis
                    if job.custom_id:
                        job_to_delete = "job_" + job.custom_id
                        redis.connect.lrem("running_jobs", 0, job_to_delete)
                        redis.connect.delete("job_" + job.custom_id)
                    else:
                        job_to_delete = "job_" + job.uuid
                        redis.connect.lrem("running_jobs", 0, job_to_delete)
                        redis.connect.delete("job_" + job.uuid)
