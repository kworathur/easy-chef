from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from django.contrib.auth import get_user_model
import os.path

class CreateUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=get_user_model().objects.all(),
                                                               message="User with this email already exists.")])

    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User # replace with get_user_model()
        fields = ['email', 'password', 'password2']

        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
        }

    def validate(self, data):
        password1 = data.get('password')
        password2 = data.get('password2')

        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError("The two passwords do not match")

        return data

    def create(self, validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True,
                                   validators=[UniqueValidator(queryset=get_user_model().objects.all(),
                                                               message="User with this email already exists.")])


    password2 = serializers.CharField(required=False, write_only=True, style={"input_type": "password"})

    class Meta:
        model = User  # replace with get_user_model()
        fields = ['first_name', 'last_name', 'email', 'avatar', 'phone_number', 'password', 'password2']

        extra_kwargs = {
            "password": {"required": False, "write_only": True, "style": {"input_type": "password"}},
        }

    def validate(self, data):

        password1 = data.get('password')
        password2 = data.get('password2')

        if (password1 or password2) and password1 != password2:
            raise serializers.ValidationError('The two passwords do not match')

        return data


    def validate_avatar(self, value):

        if self.instance and os.path.basename(str(self.instance.avatar)) == str(value):
            return None

        return value


    def update(self, instance, validated_data):

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.avatar = validated_data.get('avatar') or instance.avatar

        new_password = validated_data.get('password')
        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance





