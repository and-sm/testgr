from django.db import models
from tools.tools import normalize_time
from django.core.exceptions import ObjectDoesNotExist


class Environments(models.Model):
    name = models.TextField(blank=True, null=True)
    remapped_name = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.remapped_name:
            self.remapped_name = self.remapped_name.strip(" ")
            super(Environments, self).save(*args, **kwargs)
        else:
            super(Environments, self).save(*args, **kwargs)


class TestJobs(models.Model):
    uuid = models.CharField(max_length=255, db_index=True)
    # status: 1 "In progress", 2 - "Passed", 3 - "Failed", 4 - "Stopped"
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    env = models.ForeignKey(Environments, on_delete=models.CASCADE, related_name='environment')
    fw_type = models.SmallIntegerField(blank=True, null=True)
    tests_passed = models.SmallIntegerField(blank=True, null=True)
    tests_failed = models.SmallIntegerField(blank=True, null=True)
    tests_skipped = models.SmallIntegerField(blank=True, null=True)
    tests_aborted = models.SmallIntegerField(blank=True, null=True)
    tests_not_started = models.SmallIntegerField(blank=True, null=True)
    tests_in_progress = models.SmallIntegerField(blank=True, null=True)

    def get_time_taken(self):
        try:
            obj = normalize_time(self.time_taken)
            return obj
        except ObjectDoesNotExist:
            return None

    def get_start_time(self):
        return self.start_time.strftime('%H:%M:%S %d-%b-%Y')

    def get_stop_time(self):
        return self.stop_time.strftime('%H:%M:%S %d-%b-%Y')

    def get_env(self):
        if self.env.remapped_name:
            return self.env.remapped_name
        return self.env.name

    def tests_percentage(self):

        tests_passed = (0 if self.tests_passed is None else self.tests_passed)
        tests_failed = (0 if self.tests_failed is None else self.tests_failed)
        tests_aborted = (0 if self.tests_aborted is None else self.tests_aborted)
        tests_skipped = (0 if self.tests_skipped is None else self.tests_skipped)
        tests_not_started = (0 if self.tests_not_started is None else self.tests_not_started)

        tests_count = tests_passed + tests_not_started + tests_aborted + tests_failed + tests_skipped

        passed_percent = float(0 if tests_passed == 0 else ((tests_passed * 100) / tests_count))
        failed_percent = float(0 if tests_failed == 0 else ((tests_failed * 100) / tests_count))
        aborted_percent = float(0 if tests_aborted == 0 else ((tests_aborted * 100) / tests_count))
        skipped_percent = float(0 if tests_skipped == 0 else ((tests_skipped * 100) / tests_count))
        not_started_percent = float(0 if tests_not_started == 0 else ((tests_not_started * 100) / tests_count))

        return{"passed_percent": passed_percent,
               "failed_percent": failed_percent,
               "aborted_percent": aborted_percent,
               "skipped_percent": skipped_percent,
               "not_started_percent": not_started_percent,
               "passed_percent_float": format(passed_percent, ".2f"),
               "failed_percent_float": format(failed_percent, ".2f"),
               "aborted_percent_float": format(aborted_percent, ".2f"),
               "skipped_percent_float": format(skipped_percent, ".2f"),
               "not_started_percent_float": format(not_started_percent, ".2f")
               }


class TestsStorage(models.Model):
    identity = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    test = models.TextField(blank=True, null=True)
    fw_type = models.SmallIntegerField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    time_taken2 = models.DurationField(blank=True, null=True)
    time_taken3 = models.DurationField(blank=True, null=True)
    calculated_eta = models.DurationField(blank=True, null=True)

    def get_time_taken_eta(self):
        try:
            result = normalize_time(self.calculated_eta)
            return result
        except ObjectDoesNotExist:
            return None

    def get_test_method_for_nose(self):
        try:
            self.method = self.identity.split('.')
            self.method = self.method[-1]  # + " [" + self.method[-2] + "]"
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method

    def get_test_method_for_pytest(self):
        try:
            if "()" in self.identity:
                self.method = self.identity.split('::')
            else:
                self.method = self.identity.split('::')
            self.method = self.method[-1]  # + " [" + self.method[0] + "]"
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method


class Tests(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    # status: 1 -   "Not started" 2 - "In progress", 3 - "Passed", 4 - "Failed", 5 - "Skipped", 6 - "Aborted"
    status = models.SmallIntegerField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    job = models.ForeignKey(TestJobs, on_delete=models.CASCADE, related_name='tests')
    test = models.ForeignKey(TestsStorage, on_delete=models.CASCADE, related_name='test_storage')

    def get_start_time(self):
        return self.start_time.strftime('%H:%M:%S')

    def get_time_taken(self):
        try:
            obj = normalize_time(self.time_taken)
            return obj
        except ObjectDoesNotExist:
            return None


