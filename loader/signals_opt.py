from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def send_job_tests_details(created, instance):

    def data():
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
            test_item['time_taken_eta'] = instance.test.get_time_taken_eta()
        except:
            test_item['time_taken_eta'] = None
        test_item['status'] = instance.status

        result['test'] = test_item
        result['test_count'] = str(instance.job.tests.count())
        result['not_started'] = str(instance.job.tests.filter(status=1).count())
        result['passed'] = str(instance.job.tests.filter(status=3).count())
        result['failed'] = str(instance.job.tests.filter(status=4).count())
        result['skipped'] = str(instance.job.tests.filter(status=5).count())
        result['aborted'] = str(instance.job.tests.filter(status=6).count())
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
