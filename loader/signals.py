from django.db.models.signals import post_save
from django.dispatch import receiver

from loader.models import TestJobs, Tests

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=TestJobs)
def get_running_jobs_count(created, instance, **kwargs):

    def running_jobs_count():
        count = TestJobs.objects.filter(status='1').count()
        if count > 0:
            return count
        else:
            return None

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs_count",
            {
                "type": "message",
                "message": running_jobs_count()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs_count",
            {
                "type": "message",
                "message": running_jobs_count()
            }
        )


@receiver(post_save, sender=TestJobs)
def get_running_jobs(created, instance, **kwargs):

    def running_jobs():
        objects = TestJobs.objects.filter(status='1').order_by('-start_time')
        result = []
        for job in objects:
            job_item = dict()
            job_item['uuid'] = job.uuid
            job_item['start_time'] = job.start_time.strftime('%H:%M:%S %d-%b-%Y')
            job_item['status'] = job.status
            job_item['env'] = job.env
            result.append(job_item)
        result.reverse()  # For correct ordering in JS
        return result

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs",
            {
                "type": "message",
                "message": running_jobs()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs",
            {
                "type": "message",
                "message": running_jobs()
            }
        )


@receiver(post_save, sender=TestJobs)
def get_latest_jobs(created, instance, **kwargs):

    def latest_jobs():
        latest_jobs = TestJobs.objects.all().order_by('-stop_time').exclude(status='1')[:10]
        result = []
        for job in latest_jobs:
            job_item = dict()
            job_item['uuid'] = job.uuid
            job_item['time_taken'] = job.get_time_taken()
            job_item['stop_time'] = job.stop_time.strftime('%H:%M:%S %d-%b-%Y')
            job_item['status'] = job.status
            job_item['env'] = job.env
            result.append(job_item)
        result.reverse()  # For correct ordering in JS
        return result

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "latest_jobs",
            {
                "type": "message",
                "message": latest_jobs()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "latest_jobs",
            {
                "type": "message",
                "message": latest_jobs()
            }
        )


@receiver(post_save, sender=TestJobs)
def get_job_details(created, instance, **kwargs):

    def data():
        job_object = TestJobs.objects.get(uuid=instance.uuid)
        result = {}

        # Statistics
        if job_object.stop_time is not None:
            result['stop_time'] = job_object.stop_time.strftime('%H:%M:%S %d-%b-%Y')
        else:
            result['stop_time'] = None
        if job_object.time_taken is not None:
            result['time_taken'] = job_object.get_time_taken()
        else:
            result['time_taken'] = None

        result['status'] = str(job_object.status)

        return result

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_details",
            {
                "type": "message",
                "message": data()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_details",
            {
                "type": "message",
                "message": data()
            }
        )


@receiver(post_save, sender=Tests)
def get_job_tests_details(created, instance, **kwargs):

    def data():
        job_object = TestJobs.objects.get(uuid=instance.job.uuid)
        result = {}

        # Tests
        tests = []
        for test in job_object.tests.all():
            test_item = dict()
            if job_object.fw_type == 1:
                test_item['short_identity'] = test.get_test_method_for_nose()
            elif job_object.fw_type == 2:
                test_item['short_identity'] = test.get_test_method_for_pytest()
            test_item['identity'] = test.identity
            test_item['uuid'] = test.uuid
            test_item['time_taken'] = test.get_time_taken()
            test_item['status'] = test.status
            tests.append(test_item)
        tests.reverse()  # For correct ordering in JS
        result['tests'] = tests

        result['test_count'] = str(job_object.tests.count())
        result['not_started'] = str(job_object.tests.filter(status=1).count())
        result['passed'] = str(job_object.tests.filter(status=3).count())
        result['failed'] = str(job_object.tests.filter(status=4).count())
        result['skipped'] = str(job_object.tests.filter(status=5).count())
        result['aborted'] = str(job_object.tests.filter(status=6).count())

        return result

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_tests_details",
            {
                "type": "message",
                "message": data()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_tests_details",
            {
                "type": "message",
                "message": data()
            }
        )