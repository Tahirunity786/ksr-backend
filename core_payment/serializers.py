from rest_framework import serializers

from core_payment.models import Receipts

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipts
        fields = ("receipt_id", "student", "tutor", "price")
        