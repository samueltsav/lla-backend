from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    uid = serializers.IntegerField(source="id", read_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = "__all_"

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "dob",
            "cor",
            "nationality",
            "photo",
            "last_login",
            "dor",
            "updated_at",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = [
            "uid",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "dor",
            "updated_at",
        ]


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
