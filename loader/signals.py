from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from loader.models import TestJobs, Tests, TestsStorage, Environments

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
            job_item['tests_passed'] = job.tests_passed
            job_item['tests_failed'] = job.tests_failed
            job_item['tests_aborted'] = job.tests_aborted
            job_item['tests_skipped'] = job.tests_skipped
            job_item['tests_not_started'] = job.tests_not_started
            try:
                obj = Environments.objects.get(name=job.env.name)
                if obj.remapped_name is not None:
                    job_item['env'] = obj.remapped_name
                else:
                    job_item['env'] = obj.name
            except ObjectDoesNotExist:
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
            job_item['tests_passed'] = job.tests_passed
            job_item['tests_failed'] = job.tests_failed
            job_item['tests_aborted'] = job.tests_aborted
            job_item['tests_skipped'] = job.tests_skipped
            job_item['tests_not_started'] = job.tests_not_started
            job_item['tests_percentage'] = job.tests_percentage()
            try:
                obj = Environments.objects.get(name=job.env.name)
                if obj.remapped_name is not None:
                    job_item['env'] = obj.remapped_name
                else:
                    job_item['env'] = obj.name
            except ObjectDoesNotExist:
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
            "job_details" + "-" + instance.uuid,
            {
                "type": "message",
                "message": data()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_details" + "-" + instance.uuid,
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
            if test.start_time:  # Initial Tests post_save signal will not have start_time for test item
                test_item['start_time'] = test.get_start_time()
            if job_object.fw_type == 1:
                test_item['short_identity'] = test.test.get_test_method_for_nose()
            elif job_object.fw_type == 2:
                test_item['short_identity'] = test.test.get_test_method_for_pytest()
            test_item['identity'] = test.test.identity
            test_item['uuid'] = test.uuid
            if test.time_taken:
                test_item['time_taken'] = test.get_time_taken()
            else:
                test_item['time_taken'] = None
            try:
                obj = TestsStorage.objects.get(pk=test.test_id)
                test_item['time_taken_eta'] = obj.get_time_taken_eta()
            except:
                test_item['time_taken_eta'] = None
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
            "job_tests_details" + "-" + instance.job.uuid,
            {
                "type": "message",
                "message": data()
            }
        )

    if instance:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "job_tests_details" + "-" + instance.job.uuid,
            {
                "type": "message",
                "message": data()
            }
        )