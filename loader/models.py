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
    uuid = models.CharField(max_length=256)
    # status: 1 "In progress", 2 - "Passed", 3 - "Failed", 4 - "Stopped"
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    env = models.ForeignKey(Environments, on_delete=models.CASCADE, related_name='environment')
    fw_type = models.SmallIntegerField(blank=True, null=True)

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
        if self.env:
            try:
                obj = Environments.objects.get(name=self.env.name)
                if obj.remapped_name:
                    return obj.remapped_name
                else:
                    return self.env.name
            except ObjectDoesNotExist:
                return self.env.name
        else:
            return 'not set'


class TestsStorage(models.Model):
    identity = models.TextField(blank=True, null=True)
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
                self.method = self.method[-1]  # + " [" + self.method[1] + "]"
            else:
                self.method = self.identity.split('::')
                self.method = self.method[-1]  # + " [" + self.method[0] + "]"
        except BaseException:  # if for some reason we haven't full identity - for example "test_method".
            return self.identity
        return self.method


class Tests(models.Model):
    uuid = models.CharField(max_length=256)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.DurationField(blank=True, null=True)
    # status: 1 -   "Not started" 2 - "In progress", 3 - "Passed", 4 - "Failed", 5 - "Skipped", 6 - "Aborted"
    status = models.SmallIntegerField(blank=True, null=True)
    msg = models.TextField(blank=True)
    # fw_type = models.SmallIntegerField(blank=True, null=True)
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


