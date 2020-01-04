from rest_framework import serializers
from loader.models import Environments, TestJobs


class EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environments
        fields = ['name', 'remapped_name']


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestJobs
        fields = ['uuid']
