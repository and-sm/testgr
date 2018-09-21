from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from loader.models import TestJobs, Tests
from tools.tools import unix_time_to_datetime

import json
import uuid


@csrf_exempt
def loader(request):

    if request.method == 'GET':
        return HttpResponse("Incorrect request")
    elif request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        # Data with new Test Run
        if 'startTestRun' in data['type']:
            # print("DBG: startTestRun")
            if TestJobs.objects.filter(uuid=data['job_id']):
                return HttpResponse(status=409)
            job_object = TestJobs(uuid=data['job_id'], status=1, start_time=unix_time_to_datetime(data['startTime']),
                                  env=data['env'])
            job_object.save()
            # Tests
            for k, identity in data['tests'].items():
                test_uuid = str(uuid.uuid4())
                test_object = Tests(uuid=test_uuid, identity=identity, status=1, job=job_object)
                test_object.save()
            return HttpResponse(status=200)
        elif 'stopTestRun' in data['type']:
            # print("DBG: stopTestRun")
            try:
                job_object = TestJobs.objects.get(uuid=data['job_id'])
                # in case if 'stopTestRun' was caught, by some running test exists
                if job_object.tests.filter(status=2).first():
                    job_object.tests.filter(status=2).update(status=6)   # 'In progress' tests become 'Aborted'
                    job_object.status = 3
                # in case if 'stopTestRun' was caught and at least one test is failed
                elif job_object.tests.filter(status=4).first():
                    job_object.status = 3
                # if no tests with 'failed' or 'running' states after 'stopTestRun' signal - mark job as 'Passed'
                else:
                    job_object.status = 2
                job_object.stop_time = unix_time_to_datetime(data['stopTime'])
                job_object.time_taken = job_object.stop_time - job_object.start_time
                job_object.tests_success = data['tests_success']
                job_object.tests_errors = data['tests_errors']
                job_object.tests_failed = data['tests_failed']
                job_object.tests_skipped = data['tests_skipped']
                job_object.save()
                return HttpResponse(status=200)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        elif data['type'] == 'startTest':
            # print("DBG: startTest")
            try:
                job_object = TestJobs.objects.get(uuid=data['job_id'])
                try:
                    test = Tests.objects.get(identity=data['test'], job=job_object)
                    test.status = 2
                    test.start_time = unix_time_to_datetime(data['startTime'])
                    test.save()
                    return HttpResponse(status=200)
                except ObjectDoesNotExist:
                    return HttpResponse(status=403)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        elif 'stopTest' in data['type']:
            # print("DBG: stopTest")
            try:
                job_object = TestJobs.objects.get(uuid=data['job_id'])
                try:
                    test = Tests.objects.get(identity=data['test'], job=job_object)
                    test.stop_time = unix_time_to_datetime(data['stopTime'])
                    test.time_taken = test.stop_time - test.start_time
                    if data['status'] == "passed":
                        test.status = 3
                    elif data['status'] == "error":
                        test.status = 4
                    elif data['status'] == "failed":
                        test.status = 4
                    elif data['status'] == "skipped":
                        test.status = 5
                    test.msg = data['msg']
                    test.save()
                    return HttpResponse(status=200)
                except ObjectDoesNotExist:
                    return HttpResponse(status=403)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=403)
