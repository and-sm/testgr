from django.db import models
from tools.tools import normalize_unix_time


class TestJobs(models.Model):
    uuid = models.CharField(max_length=256)
    # status: 1 "In progress", 2 - "Passed", 3 - "Failed", 4 - "Stopped"
    start_time = models.FloatField(blank=True, null=True)
    stop_time = models.FloatField(blank=True, null=True)
    time_taken = models.FloatField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    env = models.TextField(blank=True, null=True)
    tests_success = models.IntegerField(blank=True, null=True)
    tests_errors = models.IntegerField(blank=True, null=True)
    tests_failed = models.IntegerField(blank=True, null=True)
    tests_skipped = models.IntegerField(blank=True, null=True)


class Tests(models.Model):
    uuid = models.CharField(max_length=256)
    identity = models.TextField(blank=True, null=True)
    start_time = models.FloatField(blank=True, null=True)
    stop_time = models.FloatField(blank=True, null=True)
    _time_taken = models.FloatField(blank=True, null=True, db_column='time_taken')
    # status: 1 -   "Not started" 2 - "In progress", 3 - "Passed", 4 - "Failed", 5 - "Skipped", 6 - "Aborted"
    status = models.SmallIntegerField(blank=True, null=True)
    msg = models.TextField(blank=True)
    job = models.ForeignKey(TestJobs, on_delete=models.CASCADE, related_name='tests')

    def get_test_method(self):
        try:
            self.method = self.identity.split('.')[-2]
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method

    @property
    def time_taken(self):
        if self._time_taken is not None:
            time_taken_normalized = normalize_unix_time(self._time_taken, remove_date=True)
        else:
            return None
        return time_taken_normalized

    @time_taken.setter
    def time_taken(self, value):
        self._first_name = value
