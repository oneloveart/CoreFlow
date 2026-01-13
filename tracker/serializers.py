from rest_framework import serializers
from .models import ActivityEntry

class ActivityEntrySerializer(serializers.ModelSerializer):
    duration_minutes = serializers.IntegerField(read_only=True)
    class Meta:
        model = ActivityEntry
        fields = '__all__'
