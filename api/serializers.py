from rest_framework import serializers
from loader.models import Environments, Bugs, TestsStorage, TestJobs
from management.models import Settings


class EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environments
        fields = ['name', 'remapped_name']


class TestsStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestsStorage
        fields = ['note', 'suppress']


class BugsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bugs
        fields = ['id', 'bug']


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['running_jobs_age']

