from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(source='dob')

    class Meta:
        model = CustomUser
        fields = ["id", "email", "password", "date_of_birth", "profile_image"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()

        return user


class MeSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(source='dob')

    class Meta:
        model = CustomUser
        fields = ["id", "name", "email", "gender", "date_of_birth", "profile_image"]
