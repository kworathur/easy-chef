from rest_framework import serializers
from .models import RatingRecord

class RatingRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatingRecord
        fields = ['user', 'rating', 'recipe']

    def update(self, instance, validated_data):

        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance
