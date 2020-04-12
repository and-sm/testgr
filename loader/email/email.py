from django.conf import settings
from django.core.mail import EmailMessage
import uuid  # https://stackoverflow.com/a/50055815
import json


class SendJobReport:

    def __init__(self, job):
        self.job = job
        self.non_suppress_list = list()

    def head_content(self):

        return "<!DOCTYPE html><html><head></head><body>"

    def job_content(self):
        return "<h2 style='color: #2e6c80;'>" \
               "<a href='" + settings.TESTGR_URL + "/job/" + self.job.uuid + "'>Automation Report</a></h2>" \
               "<hr />" \
               "<p class='small'><strong>Environment: </strong>" + str(self.job.get_env()) + "</p>" \
               "<p class='small'><strong>Date Started: </strong>" \
               "" + str(self.job.get_start_time()) + "</p>" \
               "<p class='small'><strong>Date Finished: </strong>" \
               "" + str(self.job.get_stop_time()) + "</p>" \
               "<p class='small'><strong>Duration: </strong>" + self.job.get_time_taken() + "</p>"

    def custom_data(self):
        if self.job.custom_data:
            custom_data_items = list()
            custom_data = json.loads(self.job.custom_data)
            for k, v in custom_data.items():
                custom_data_items.append("<p class='small'><strong>" + k + ": </strong>" + v + "</p>")
            return "".join(custom_data_items)
        return ""

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
                suppress = test.test.get_suppress()
                if not suppress:
                    self.non_suppress_list.append(suppress)
                if self.job.fw_type == 1:
                    method = test.test.get_test_method_for_nose()
                elif self.job.fw_type == 2:
                    method = test.test.get_test_method_for_pytest()
                else:
                    method = ''

                bugs = test.test.get_bugs()
                if bugs:
                    bugs_list = list()
                    for bug, btype in bugs.items():
                        bugs_list.append(bug)
                    bug_items = " ".join(item for item in bugs_list)
                    td_note = "<td style='padding: 8px;text-align: left;border-bottom: 1px solid #ddd;'>" \
                              + bug_items + "</td>"
                else:
                    td_note = "<td style='padding: 8px;text-align: left;border-bottom: 1px solid #ddd;'></td>"

                tests_data.append(str("<tr><td style='padding: 8px;text-align: left;border-bottom: 1px solid #ddd;'>"
                                      + method + "</td>" + td_note + "</tr>"))

        suppressed = failed - (len(self.non_suppress_list))
        if suppressed > 0:
            suppressed = " (muted: " + str(suppressed) + ")"
        else:
            suppressed = ""

        tests_data = ''.join(tests_data)
        count_data = "<h3>Tests: " + str(len(tests)) + "</h3><h4>Passed: <span style='color: green;'>" + str(passed) + \
                     "</span>, Failed: <span style='color: red;'>" + str(failed) + "</span>" + suppressed + \
                     ", Skipped: <span style='color: gray;'>" + str(skipped) + "</span></h4>"

        return count_data + "<table style='border-collapse: collapse;width: 20%;'><tbody>" + tests_data

    def tests_content_table_footer(self):
        return "</tbody></table>"

    def footer_content(self):
        if len(self.non_suppress_list) < 1:
            suppress_msg = "<p></p><strong>Part of tests was muted by users.</strong>"
        else:
            suppress_msg = ""
        return suppress_msg + "<p></p><a href='" + settings.TESTGR_URL + "/job/" + \
               str(self.job.uuid) + "'>Click to read full details</a></p>" \
                                    "<span style=\"opacity: 0\">" + str(uuid.uuid4()) + "</span></body></html>"

    def message(self):
        return self.head_content() + self.job_content() + self.custom_data() + self.tests_content() + \
               self.tests_content_table_footer() + self.footer_content()

    def send(self):
        receivers = settings.EMAIL_RECEIVER
        if "," in receivers:
            receivers = receivers.split(",")
        else:
            receivers = [receivers]

        body = self.message()

        if settings.EMAIL_SUBJECT:
            subject = settings.EMAIL_SUBJECT
        else:
            if len(self.non_suppress_list) > 0:
                overall_status = "FAILED"
            else:
                overall_status = "OK"
            subject = "Automation Report: " + overall_status
        """
                    subject = str("Automation Report:  Passed ") + str(self.job.tests.filter(status=3).count()) \
                      + ", Failed " + str(self.job.tests.filter(status=4).count()) \
                      + ", Skipped " + str(self.job.tests.filter(status=5).count())
        """
        email = EmailMessage(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=receivers,
            body=body
        )
        email.content_subtype = "html"
        email.send()
