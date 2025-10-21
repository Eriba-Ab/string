from rest_framework import serializers
from .models import StringEntry


class StringEntrySerializer(serializers.ModelSerializer):
	class Meta:
		model = StringEntry
		fields = ['id', 'value', 'properties', 'created_at']