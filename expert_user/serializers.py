from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import serializers

from expert_order.models import Order
from expert_user.models import ExUser


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=32)

    class Meta:
        model = ExUser
        fields = "__all__"

    def validate(self, attrs):

        username = attrs.get('username')
        phone = attrs.get('phone_num')
        password = attrs.get('password')

        if not username:
            msg = "Username must set"
            raise serializers.ValidationError(msg, code=400)

        if not phone:
            msg = 'Phone number must set'
            raise serializers.ValidationError(msg, code=400)

        if not password:
            msg = 'Password must set'
            raise serializers.ValidationError(msg, code=400)

        return attrs


class ResetPassSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(label="OldPassword",
                                         style={'input_type': 'password'},
                                         trim_whitespace=False)
    new_password = serializers.CharField(label='NewPassword',
                                         style={'input_type': 'password'},
                                         trim_whitespace=False)
    confirm_password = serializers.CharField(label='ConfirmPassword',
                                             style={'input_type': 'password'},
                                             trim_whitespace=False)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if old_password and new_password and confirm_password:
            if not (new_password == confirm_password):
                msg = "Passwords are different, reconfirm again"
                raise serializers.ValidationError(msg, code=400)
            elif new_password == old_password:
                msg = "New password is same as old password"
                raise serializers.ValidationError(msg, code=400)
        else:
            msg = "OldPassword, NewPassword and ConfirmPassword are required"
            raise serializers.ValidationError(msg, code=400)
        return attrs


class UploadAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(allow_empty_file=False, use_url=True)
    suffix = serializers.CharField(allow_blank=False)

    class Meta:
        model = ExUser
        fields = ['avatar', 'suffix']


class UserInformationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')
    user_id = serializers.CharField(source='user.id')

    class Meta:
        model = ExUser
        fields = '__all__'


class UserInformationModifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExUser
        exclude = ('user', 'avatar')
