from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from tools.tools import get_hash, compare_hash
from loader.models import TestJobs, Tests, TestsStorage
from loader.redis import Redis

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import time
from operator import itemgetter


@receiver(post_save, sender=TestJobs)
def get_running_jobs_count(created, instance, **kwargs):

    def running_jobs_count():
        redis = Redis()
        job_list_from_redis = redis.connect.lrange("running_jobs", 0, -1)
        job_list = list()
        for item in job_list_from_redis:
            job_list.append(item.decode("utf-8"))
        count = len(job_list)
        if count > 0:
            return count
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

    def update_running_jobs():  # fix for newly created job, it should appear in the Running Jobs table right after creation
        redis = Redis()
        if redis.connect.exists("update_running_jobs"):
            redis.connect.delete("update_running_jobs")
            return True

    def send_data():
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs",
            {
                "type": "message",
                "message": running_jobs_result[0]
            }
        )

    def running_jobs():
        update_running_jobs = None
        redis = Redis()

        # Checking all *job_ keys
        data = redis.connect.keys("job_*")
        active_jobs = list()
        for job_item in data:
            data = redis.get_value_from_key_as_str(job_item)
            active_jobs.append(data)
        # https://www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-itemgetter/

        result = sorted(active_jobs, key=itemgetter('start_time'))

        # Getting "latest_jobs" key for future time comparison
        redis_latest_jobs_time = redis.get_value_from_key_as_str("latest_jobs_time")
        if redis_latest_jobs_time is not None:
            timestamp = time.time()
            time_result = timestamp - redis_latest_jobs_time
            if time_result > 3:
                redis.set_value("latest_jobs_time", str(time.time()))  # send updated time
                update_running_jobs = True
        else:
            redis_latest_jobs_time = time.time()
            redis.set_value("latest_jobs_time", str(redis_latest_jobs_time))  # send updated time
            update_running_jobs = False

        if update_running_jobs is True:
            return result, True
        else:
            return result, False

    if created:
        running_jobs_result = running_jobs()
        if running_jobs_result[1] is True:
            send_data()
        else:
            pass

    if instance.status == 1:
        running_jobs_result = running_jobs()
        if running_jobs_result[1] is True:
            send_data()
        elif update_running_jobs():
            send_data()
        else:
            pass

    if instance.status != 1:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "running_jobs",
            {
                "type": "message",
                "message": {"job_remove": instance.uuid}
            }
        )


@receiver(post_save, sender=TestJobs)
def get_latest_jobs(created, instance, **kwargs):

    def latest_jobs():
        # Redis, getting "latest_jobs" key for future hash comparison
        redis = Redis()
        redis_latest_jobs_hash = redis.get_value_from_key_as_str("latest_jobs")

        latest_jobs_q = TestJobs.objects.select_related('env').order_by('-stop_time').exclude(status='1')[:10]
        result = []
        list_for_hash = []
        for job in latest_jobs_q:
            job_item = dict()
            job_item['uuid'] = job.uuid
            job_item['time_taken'] = job.get_time_taken()
            job_item['stop_time'] = timezone.localtime(job.stop_time).strftime('%d-%b-%Y, %H:%M:%S')
            if job.status == 4:  # special case for show "skipped" label while websocket updates "Last Jobs table"
                job_item['status'] = 4
            if job.tests_passed is not None:
                job_item['tests_passed'] = job.tests_passed
            if job.tests_failed is not None:
                job_item['tests_failed'] = job.tests_failed
            if job.tests_aborted is not None:
                job_item['tests_aborted'] = job.tests_aborted
            if job.tests_skipped is not None:
                job_item['tests_skipped'] = job.tests_skipped
            if job.tests_not_started != 0:
                job_item['tests_not_started'] = job.tests_not_started
            job_item['tests_percentage'] = job.tests_percentage()
            job_item['env'] = job.get_env()
            job_item['status'] = job.status
            list_for_hash.append(job.uuid)  # building list with job uuid's for making local hash of all our latest jobs
            result.append(job_item)
        result_hash = get_hash(frozenset(list_for_hash))    # hash of local job uuid's
        redis.set_value("latest_jobs", result_hash)   # send update hash value to Redis
        result.reverse()  # For correct ordering in JS

        # Compare between Redis previous hash and local hash of latest_jobs
        if compare_hash(redis_latest_jobs_hash, result_hash):
            # Hash identical
            return result, True
        else:
            # Hash NOT identical
            return result, False

    if created:
        latest_jobs_result = latest_jobs()
        if latest_jobs_result[1] is False:     # If hashes are NOT identical - send update via websocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "latest_jobs",
                {
                    "type": "message",
                    "message": latest_jobs_result[0]
                }
            )
        else:   # Hashes are identical - no websocket update is needed
            pass

    if instance:
        latest_jobs_result = latest_jobs()
        if latest_jobs_result[1] is False:     # If hashes are NOT identical - send update via websocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "latest_jobs",
                {
                    "type": "message",
                    "message": latest_jobs_result[0]
                }
            )
        else:   # Hashes are identical - no websocket update is needed
            pass


@receiver(post_save, sender=TestJobs)
def get_job_details(created, instance, **kwargs):

    def data():
        job_object = TestJobs.objects.get(uuid=instance.uuid)
        result = {}

        # Statistics
        if job_object.stop_time is not None:
            result['stop_time'] = timezone.localtime(job_object.stop_time).strftime('%d-%b-%Y, %H:%M:%S')
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

        # Test instance update for tests table
        test_item = dict()
        test_item['uuid'] = instance.uuid
        if instance.start_time:  # Initial Tests post_save signal will not have start_time for test item
            test_item['start_time'] = instance.get_start_time()
        if instance.stop_time:
            test_item['stop_time'] = instance.get_stop_time()
        if instance.time_taken:
            test_item['time_taken'] = instance.get_time_taken()
        else:
            test_item['time_taken'] = None
        try:
            obj = TestsStorage.objects.get(pk=instance.test_id)
            test_item['time_taken_eta'] = obj.get_time_taken_eta()
        except:
            test_item['time_taken_eta'] = None
        test_item['status'] = instance.status

        result['test'] = test_item
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