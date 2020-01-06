from rest_framework import serializers
from loader.models import Environments, TestJobs, TestsStorage


class EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environments
        fields = ['name', 'remapped_name']


class TestsStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestsStorage
        fields = ['note']
