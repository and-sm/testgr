import uuid
import json

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.utils import timezone

from loader.models import TestJobs, Tests, Environments, TestsStorage
from loader.methods.common import save_images
from loader.redis import Redis
from loader.email.email_report import SendJobReport

from tools.tools import unix_time_to_datetime
from statistics import median


class PytestLoader:

    def __init__(self, data):
        self.data = data
        self.redis = Redis()

    @staticmethod
    def generate_uuid() -> str:
        value = uuid.uuid4()
        return str(value)

    def get_start_test_run(self):
        # print("DBG: startTestRun")
        # print(self.data)
        try:
            TestJobs.objects.get(uuid=self.data['job_id'])
            return HttpResponse(status=409)
        except ObjectDoesNotExist:
            pass
        try:
            env = Environments.objects.get(name=self.data['env'])
            # Env name for Redis
            env_name = env.remapped_name if env.remapped_name is not None else env.name
        except ObjectDoesNotExist:
            if self.data['env'] is not None:
                env = Environments(name=self.data['env'])
                env.save()
                # Env name for Redis
                env_name = env.remapped_name if env.remapped_name is not None else env.name
            else:
                try:
                    env = Environments.objects.get(name="None")
                    # Env name for Redis
                    if env.remapped_name:
                        env_name = env.remapped_name
                    else:
                        env_name = env.name
                except ObjectDoesNotExist:
                    env = Environments(name="None")
                    env.save()
                    # Env name for Redis
                    env_name = "None"

        # We should not create a job without tests
        if len(self.data['tests']) == 0:
            return HttpResponse(status=403)

        try:
            custom_data = json.loads(self.data["custom_data"])
        except:
            custom_data = None

        job_object = TestJobs(uuid=self.data['job_id'],
                              status=1,
                              fw_type=2,
                              start_time=unix_time_to_datetime(self.data['startTime']),
                              env=env,
                              custom_data=custom_data)
        job_object.save()

        # Tests
        tests = []
        for test_item in self.data['tests']:
            uuid = test_item['uuid']
            description = test_item['description']

            # Tests Storage
            try:
                test_storage_item = TestsStorage.objects.get(identity=test_item['nodeid'])
                # If no test obj exists
                if not test_storage_item.test:
                    test_storage_item.test = test_item['nodeid'].split('::')[-1]
                    test_storage_item.description = description
                    test_storage_item.save()
                # If test obj exists with null description
                elif test_storage_item.test and not test_storage_item.description:
                    test_storage_item.description = description
                    test_storage_item.save()
                # if test obj exists with description
                elif test_storage_item.test and test_storage_item.description:
                    if test_storage_item.description == description:
                        pass
                    else:
                        test_storage_item.description = description
                        test_storage_item.save()
            except ObjectDoesNotExist:
                test_storage_item = TestsStorage(identity=test_item['nodeid'],
                                                 test=test_item['nodeid'].split('::')[-1], description=description)
                test_storage_item.save()

            # Tests for Job
            tests.append({'test_uuid': uuid, 'status': 1, 'job': job_object.pk, 'test': test_storage_item.pk})
        with connection.cursor() as cursor:
            for test in tests:
                cursor.execute("INSERT INTO loader_tests (uuid, status, job_id, test_id)"
                               "VALUES(%s, 1, %s, %s)",
                               [test['test_uuid'], test['job'], test['test']])

        tests_not_started = job_object.tests.count()
        job_object.tests_not_started = tests_not_started
        job_object.save()

        # Redis data
        # We are creating/updating "running_jobs" list in Redis with our new job item
        job = "job_" + self.data['job_id']
        self.redis.connect.rpush("running_jobs", job)
        data = str({
            "uuid": self.data["job_id"],
            "status": "1",
            "start_time": timezone.localtime(unix_time_to_datetime(self.data['startTime']))
                .strftime('%d-%b-%Y, %H:%M:%S'),
            "tests_not_started": str(tests_not_started),
            "env": str(env_name)
        })
        self.redis.set_value("job_" + self.data['job_id'], data)
        self.redis.set_value("update_running_jobs", "1")

        return "done"

    @classmethod
    def start_test_run(cls, data):
        loader = cls(data)
        result = loader.get_start_test_run()
        return result

    def get_stop_test_run(self):
        # print("DBG: stopTestRun")
        # print(self.data)

        try:
            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            if job_object.status == 1:

                # Redis
                # Remove job uuid from "jobs" key immediately

                job = "job_" + self.data['job_id']
                self.redis.connect.lrem("running_jobs", 0, job)
                self.redis.connect.delete("job_" + self.data['job_id'])

                failed = job_object.tests_failed
                not_started = job_object.tests_not_started

                # If any "aborted" test case:
                # Job status = Aborted
                # Every "in progress" tests becomes - aborted

                tests = job_object.tests.filter(status=2)
                if job_object.tests.filter(status=6).first():
                    job_object.status = 4
                    if tests:
                        aborted_tests = 0
                        for test in tests:
                            test.status = 6
                            test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                            test.time_taken = test.stop_time - test.start_time
                            test.save()
                            aborted_tests += 1
                        job_object.tests_aborted = aborted_tests
                # If any "failed" test case:
                # Job status = Failed
                # Every "in progress" tests becomes - aborted
                elif failed:
                    job_object.status = 3
                    if tests:
                        aborted_tests = 0
                        for test in tests:
                            test.status = 6
                            test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                            test.time_taken = test.stop_time - test.start_time
                            test.save()
                            aborted_tests += 1
                        job_object.tests_aborted = aborted_tests
                elif not_started:
                    # If no "failed" test cases, but "not started" remain - job will be "Failed"
                    if tests:
                        aborted_tests = 0
                        for test in tests:
                            test.status = 6
                            test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                            test.time_taken = test.stop_time - test.start_time
                            test.save()
                            aborted_tests += 1
                        job_object.tests_aborted = aborted_tests
                    job_object.status = 3
                # Bug fix - abort scenario with single test
                elif tests:
                    aborted_tests = 0
                    for test in tests:
                        test.status = 6
                        test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                        test.time_taken = test.stop_time - test.start_time
                        test.save()
                        aborted_tests += 1
                    job_object.tests_aborted = aborted_tests
                    job_object.status = 3
                # If no "failed" (and other negative variations) test cases - job will be "Passed"
                else:
                    job_object.status = 2

                job_object.stop_time = unix_time_to_datetime(self.data['stopTime'])
                job_object.time_taken = job_object.stop_time - job_object.start_time

                job_object.save()
                if self.data['send_report'] == "1":
                    SendJobReport(job_object).send()
                return "done"
            else:
                return HttpResponse(status=403)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)

    @classmethod
    def stop_test_run(cls, data):
        loader = cls(data)
        result = loader.get_stop_test_run()
        return result

    def get_start_test(self):
        # print("DBG: startTest")
        # print(self.data)
        try:

            # Redis
            # Job item update
            data = self.redis.get_value_from_key_as_str("job_" + self.data['job_id'])
            if data is None:
                return HttpResponse(status=403)
            tests_not_started = int(data["tests_not_started"])
            tests_not_started -= 1
            data["tests_not_started"] = str(tests_not_started)
            data = str(data).encode("utf-8")
            self.redis.set_value("job_" + self.data['job_id'], data)

            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            job_object.tests_not_started -= 1
            if job_object.tests_not_started == 0:
                job_object.tests_not_started = None

            job_object.tests_in_progress = 1

            job_object.save()

            if job_object.status == 1:
                try:
                    test = Tests.objects.get(uuid=self.data['uuid'])
                    test.status = 2
                    test.start_time = unix_time_to_datetime(self.data['startTime'])
                    test.save()
                    return "done"
                except ObjectDoesNotExist:
                    return HttpResponse(status=403)
            else:
                return HttpResponse(status=403)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)

    @classmethod
    def start_test(cls, data):
        loader = cls(data)
        result = loader.get_start_test()
        return result

    def get_stop_test(self):
        # print("DBG: stopTest")
        # print(self.data)
        try:

            # Redis
            # Job item update

            data = self.redis.get_value_from_key_as_str("job_" + self.data['job_id'])
            if data is None:
                return HttpResponse(status=403)
            job_object = TestJobs.objects.get(uuid=self.data['job_id'])
            if job_object.status == 1:
                try:
                    test = Tests.objects.get(uuid=self.data['uuid'])
                    if self.data['status'] == "passed":
                        test.status = 3
                        if not job_object.tests_passed:
                            job_object.tests_passed = 1
                            data["tests_passed"] = str(1)
                        else:
                            job_object.tests_passed += 1
                            data["tests_passed"] = str(job_object.tests_passed)
                    elif self.data['status'] == "error":
                        test.status = 4
                        if not job_object.tests_failed:
                            job_object.tests_failed = 1
                            data["tests_failed"] = str(1)
                        else:
                            job_object.tests_failed += 1
                            data["tests_failed"] = str(job_object.tests_failed)
                    elif self.data['status'] == "failed":
                        test.status = 4
                        if not job_object.tests_failed:
                            job_object.tests_failed = 1
                            data["tests_failed"] = str(1)
                        else:
                            job_object.tests_failed += 1
                            data["tests_failed"] = str(job_object.tests_failed)
                    elif self.data['status'] == "skipped":
                        test.status = 5
                        if not job_object.tests_skipped:
                            job_object.tests_skipped = 1
                            data["tests_skipped"] = str(1)
                        else:
                            job_object.tests_skipped += 1
                            data["tests_skipped"] = str(job_object.tests_skipped)

                    job_object.tests_in_progress = None

                    data = str(data).encode("utf-8")
                    self.redis.set_value("job_" + self.data['job_id'], data)

                    job_object.save()

                    test.stop_time = unix_time_to_datetime(self.data['stopTime'])
                    test.time_taken = test.stop_time - test.start_time
                    test.msg = str(self.data['msg']).replace("\\n", "\n")

                    # Save image artifacts if exist
                    save_images(self, test)

                    test.save()

                    # Tests Storage
                    obj = TestsStorage.objects.get(pk=test.test_id)
                    if not obj.time_taken:
                        obj.time_taken = test.time_taken
                        obj.calculated_eta = median([obj.time_taken, test.time_taken])
                        obj.save()
                        return "done"
                    if obj.time_taken and not obj.time_taken2:
                        obj.time_taken2 = test.time_taken
                        obj.calculated_eta = median([obj.time_taken, obj.time_taken2])
                        obj.save()
                        return "done"
                    if obj.time_taken2 and not obj.time_taken3:
                        obj.time_taken3 = test.time_taken
                        obj.calculated_eta = median([obj.time_taken, obj.time_taken2, obj.time_taken3])
                        obj.save()
                        return "done"
                    if obj.time_taken3:
                        obj.time_taken3 = obj.time_taken2
                        obj.time_taken2 = obj.time_taken
                        obj.time_taken = test.time_taken
                        obj.calculated_eta = median([obj.time_taken, obj.time_taken2, obj.time_taken3])
                        obj.save()
                        return "done"

                except ObjectDoesNotExist:
                    return HttpResponse(status=403)
            else:
                return HttpResponse(status=403)
        except ObjectDoesNotExist:
            return HttpResponse(status=403)

    @classmethod
    def stop_test(cls, data):
        loader = cls(data)
        result = loader.get_stop_test()
        return result