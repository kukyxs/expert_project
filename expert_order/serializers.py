from rest_framework import serializers

from expert_order.models import Order


class PublishOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_name', 'order_sum', 'order_location']


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class PickFinishOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ()


class EvaluateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('evaluation', 'grade')

    def validate(self, attrs):
        evaluation = attrs.get('evaluation')
        grade = attrs.get('grade')

        if len(evaluation.split()) < 5:
            msg = "too short"
            raise serializers.ValidationError(msg, code=400)

        if grade > 5:
            msg = "greatest grade is 5"
            raise serializers.ValidationError(msg, code=400)

        return attrs
