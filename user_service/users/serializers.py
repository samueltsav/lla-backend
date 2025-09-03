from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    uid = serializers.IntegerField(source="id", read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "uid",
            "username",
            "email",
            "phone_number",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "username",
            "email",
            "phone_number",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "dob",
            "nationality",
            "cor",
            "photo",
            "dor",
            "updated_at",
        ]
        read_only_fields = ["uid"]


class UserServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "username",
            "email",
        ]
        read_only_fields = ["uid", "username", "email"]


class MyTokenCreateSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["is_active"] = user.is_active

        return token
