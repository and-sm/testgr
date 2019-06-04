from django.conf import settings
from django.core.mail import EmailMessage
import uuid  # https://stackoverflow.com/a/50055815


class SendJobReport:

    def __init__(self, job):
        self.job = job

    def head_content(self):

        return "<!DOCTYPE html><html><head></head><body>"

    def job_content(self):
        return "<h2 style='color: #2e6c80;'>" \
               "<a href='" + settings.TESTGR_URL + "/job/" + self.job.uuid + "'>Automation Report</a></h2>" \
               "<hr />" \
               "<p class='small'><strong>Environment: </strong>" + str(self.job.env) + "</p>" \
               "<p class='small'><strong>Date Started: </strong>" \
               "" + str(self.job.get_start_time()) + "</p>" \
               "<p class='small'><strong>Date Finished: </strong>" \
               "" + str(self.job.get_stop_time()) + "</p>" \
               "<p class='small'><strong>Duration: </strong>" + self.job.get_time_taken() + "</p>"

    def tests_content(self):
        tests_data = list()
        tests = self.job.tests.all()
        passed = 0
        failed = 0
        skipped = 0
        for test in tests:
            if test.status == 3:
                passed += 1
            if test.status == 5:
                skipped += 1
            if test.status == 4:
                failed += 1
                if self.job.fw_type == 1:
                    method = test.test.get_test_method_for_nose()
                elif self.job.fw_type == 2:
                    method = test.test.get_test_method_for_pytest()
                else:
                    method = ''
                tests_data.append(str("<tr><td style='padding: 8px;text-align: left;border-bottom: 1px solid #ddd;'>"
                                      + method + "</td></tr>"))
        tests_data = ''.join(tests_data)
        count_data = "<h3>Tests: " + str(len(tests)) + "</h3><h4>Passed: <span style='color: green;'>" + str(passed) + \
                     "</span>, Failed: <span style='color: red;'>" + str(failed) + \
                     "</span>, Skipped: <span style='color: gray;'>" + str(skipped) + "</span></h4>"
        return count_data + "<table style='border-collapse: collapse;width: 30%;'><tbody>" + tests_data

    def tests_content_table_footer(self):
        return "</tbody></table>"

    def footer_content(self):
        return "<p></p><a href='" + settings.TESTGR_URL + "/job/" + \
               str(self.job.uuid) + "'>Click to read full details</a></p>" \
                                    "<span style=\"opacity: 0\">" + str(uuid.uuid4()) + "</span></body></html>"

    def message(self):
        return self.head_content() + self.job_content() + self.tests_content() + \
               self.tests_content_table_footer() + self.footer_content()

    def send(self):
        email = EmailMessage(
            subject=str("Automation report: Passed ") + str(self.job.tests.filter(status=3).count()) + ", Failed " + str(self.job.tests.filter(status=4).count()) + ", Skipped " + str(self.job.tests.filter(status=1).count()),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.EMAIL_RECEIVER],
            body=self.message()
        )
        email.content_subtype = "html"
        email.send()
