from rest_framework import serializers


class CreatePaymentOrderSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()


class VerifyPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    payment_id = serializers.CharField()
    signature = serializers.CharField()


class CapturePaymentSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
