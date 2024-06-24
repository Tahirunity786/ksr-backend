from rest_framework import serializers
from core_accounts.models import Reviews



class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ('id', 'tutor', 'reviewer', 'rating', 'reviewer_msg',)