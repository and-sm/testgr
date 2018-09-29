from django.db import models
from tools.tools import normalize_time_taken


class TestJobs(models.Model):
    uuid = models.CharField(max_length=256)
    # status: 1 "In progress", 2 - "Passed", 3 - "Failed", 4 - "Stopped"
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    env = models.TextField(blank=True, null=True)
    tests_success = models.IntegerField(blank=True, null=True)
    tests_errors = models.IntegerField(blank=True, null=True)
    tests_failed = models.IntegerField(blank=True, null=True)
    tests_skipped = models.IntegerField(blank=True, null=True)
    fw_type = models.SmallIntegerField(blank=True, null=True)

    def get_time_taken(self):
        try:
            obj = normalize_time_taken(self)
            return obj
        except BaseException:
            return None

    def get_start_time(self):
        return self.start_time.strftime('%H:%M:%S %d-%b-%Y')

    def get_stop_time(self):
        return self.stop_time.strftime('%H:%M:%S %d-%b-%Y')

    def get_env(self):
        if self.env is not None:
            return self.env
        else:
            return 'not set'


class Tests(models.Model):
    uuid = models.CharField(max_length=256)
    identity = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    # status: 1 -   "Not started" 2 - "In progress", 3 - "Passed", 4 - "Failed", 5 - "Skipped", 6 - "Aborted"
    status = models.SmallIntegerField(blank=True, null=True)
    msg = models.TextField(blank=True)
    job = models.ForeignKey(TestJobs, on_delete=models.CASCADE, related_name='tests')

    def get_test_method_for_nose(self):
        try:
            self.method = self.identity.split('.')
            self.method = self.method[-1] + " [" + self.method[-2] + "]"
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method

    def get_test_method_for_pytest(self):
        try:
            if "()" in self.identity:
                self.method = self.identity.split('::')
                self.method = self.method[-1] + " [" + self.method[1] + "]"
            else:
                self.method = self.identity.split('::')
                self.method = self.method[-1] + " [" + self.method[0] + "]"
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method

    def get_time_taken(self):
        try:
            obj = normalize_time_taken(self)
            return obj
        except BaseException:
            return None
