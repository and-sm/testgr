from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from loader.models import TestJobs, Tests
from tools.tools import unix_time_to_datetime

import uuid


class Nose2Loader:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def generate_uuid() -> str:
        value = uuid.uuid4()
        return str(value)

    def get_start_test_run(self):
        # print("DBG: startTestRun")
        # print(self.data)
        if TestJobs.objects.filter(uuid=self.data['job_id']):
            return HttpResponse(status=409)
        job_object = TestJobs(uuid=self.data['job_id'],
                              status=1,
                              fw_type=1,
                              start_time=unix_time_to_datetime(self.data['startTime']),
                              env=self.data['env'])
        job_object.save()
        # Tests
        for k, identity in self.data['tests'].items():
            test_uuid = self.generate_uuid()
            test_object = Tests(uuid=test_uuid, identity=identity, status=1, job=job_object)
            test_object.save()
        return HttpResponse(status=200)

    def get_stop_test_run(self):
        # print("DBG: stopTestRun")
        # print(self.data)
        try:
            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            # in case if 'stopTestRun' was caught, by some running test exists
            if job_object.tests.filter(status=2).first():
                job_object.tests.filter(status=2).update(status=6)  # 'In progress' tests become 'Aborted'
                job_object.status = 3
            # in case if 'stopTestRun' was caught and at least one test is failed
            elif job_object.tests.filter(status=4).first():
                job_object.status = 3
            # if no tests with 'failed' or 'running' states after 'stopTestRun' signal - mark job as 'Passed'
            else:
                job_object.status = 2
            job_object.stop_time = unix_time_to_datetime(self.data['stopTime'])
            job_object.time_taken = job_object.stop_time - job_object.start_time
            job_object.save()
            return HttpResponse(status=200)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)

    def get_start_test(self):
        # print("DBG: startTest")
        # print(self.data)
        try:
            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            try:
                test = Tests.objects.get(identity=self.data['test'], job=job_object)
                test.status = 2
                test.start_time = unix_time_to_datetime(self.data['startTime'])
                test.save()
                return HttpResponse(status=200)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)

    def get_stop_test(self):
        # print("DBG: stopTest")
        # print(self.data)
        try:
            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            try:
                test = Tests.objects.get(identity=self.data['test'], job=job_object)
                test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                test.time_taken = test.stop_time - test.start_time
                if self.data['status'] == "passed":
                    test.status = 3
                elif self.data['status'] == "error":
                    test.status = 4
                elif self.data['status'] == "failed":
                    test.status = 4
                elif self.data['status'] == "skipped":
                    test.status = 5
                test.msg = str(self.data['msg']).replace("\\n", "\n")
                test.save()
                return HttpResponse(status=200)
            except ObjectDoesNotExist:
                return HttpResponse(status=403)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)
