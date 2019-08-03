from rest_framework import serializers
from loader.models import Environments


class EnvironmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environments
        fields = ['name', 'remapped_name']
