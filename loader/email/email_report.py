import json

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template


class SendJobReport:

    settings_testgr_url = settings.TESTGR_URL

    def __init__(self, job):
        self.job = job
        self.job_start_time = job.get_start_time()
        self.job_stop_time = job.get_stop_time()
        self.job_time_taken = job.get_time_taken()
        self.job_env = job.get_env()
        self.job_uuid = job.uuid
        self.job_custom_data = job.custom_data
        self.tests = job.tests.all()
        self.overall_status = None

    def receivers(self):
        receivers = settings.EMAIL_RECEIVER
        if "," in receivers:
            return receivers.split(",")
        return [receivers]

    def get_method(self, test):
        if self.job.fw_type == 1:
            return test.get_test_method_for_nose()
        elif self.job.fw_type == 2:
            return test.test.get_test_method_for_pytest()
        else:
            return ''

    def generate_custom_data(self):
        if self.job.custom_data:
            return json.loads(self.job.custom_data)
        return ""

    def tests_builder(self):
        suppress = False
        suppress_list = list()
        failed_dict = dict()
        passed = 0
        failed = 0
        aborted = 0
        skipped = 0
        not_started = 0
        if self.job.status == 2:
            self.overall_status = "OK"
        else:
            self.overall_status = "FAILED"
        for test in self.tests:
            if test.status == 3:
                passed += 1
            if test.status == 5:
                skipped += 1
            if test.status == 4:
                failed += 1
                method = self.get_method(test.test)
                failed_dict[method] = {"suppress": bool, "bugs": bool}
                # Suppress?
                if test.test.suppress:
                    failed_dict[method]["suppress"] = True
                    suppress_list.append(1)
                # Bugs?
                bugs = test.test.get_bugs()
                failed_dict[method]["bugs"] = bugs
            if test.status == 1:
                not_started += 1
            if test.status == 6:
                aborted += 1
        suppress_count = len(suppress_list)
        if suppress_count > 0:
            suppress = True
        data = {"tests_passed": passed, "tests_failed": failed,
                "tests_skipped": skipped, "failed_tests_details": failed_dict, "suppress": suppress,
                "suppress_count": suppress_count}
        return data

    def generate_html(self):
        tests_builder = self.tests_builder()
        html = get_template("loader/email.html")
        d = {'testgr_url': self.settings_testgr_url,
             'job_uuid': self.job_uuid,
             'environment': self.job_env,
             'start_date': self.job_start_time,
             'stop_date': self.job_stop_time,
             'duration': self.job_time_taken,
             'custom_data': self.generate_custom_data(),
             'tests_total_count': len(self.tests),
             'tests_passed': tests_builder["tests_passed"],
             'tests_failed': tests_builder["tests_failed"],
             'tests_skipped': tests_builder["tests_skipped"],
             'failed_tests_details': tests_builder["failed_tests_details"],
             'suppress': tests_builder["suppress"],
             'suppress_count': tests_builder["suppress_count"]}
        html_content = html.render(d)
        return html_content

    def send(self):
        body = self.generate_html()

        if settings.EMAIL_SUBJECT:
            subject = settings.EMAIL_SUBJECT
        else:
            subject = "Automation Report: " + self.overall_status
        email = EmailMessage(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.receivers(),
            body=body
        )
        email.content_subtype = "html"
        email.send()
