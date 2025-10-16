from uuid import uuid4

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as jwt_serializers

from orderflow.users import services

User = get_user_model()


class TokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    refresh = serializers.CharField(write_only=True)


def _issue_pair_for(user):
    token = jwt_serializers.TokenObtainPairSerializer().get_token(user)
    token["username"] = user.username
    token["is_superuser"] = user.is_superuser
    return {"refresh": str(token), "access": str(token.access_token)}


# -------- Password sign-in --------
class PasswordSignInSerializer(serializers.Serializer):
    mobile = serializers.RegexField(r"^09\d{9}$", max_length=11, write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = authenticate(
            username=validated_data["mobile"], password=validated_data["password"]
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive.")
        return _issue_pair_for(user)


# -------- OTP sign-in (2 steps) --------
class MobileSignInStep1Serializer(serializers.Serializer):
    mobile = serializers.RegexField(r"^09\d{9}$", max_length=11, write_only=True)
    otp_id = serializers.CharField(read_only=True)

    def create(self, validated_data):
        username = validated_data["mobile"]
        if User.objects.filter(username=username).exists():
            otp = services.send_otp(username)
            return {"otp_id": str(otp.id)}
        return {"otp_id": str(uuid4())}


class SignInStep2Serializer(serializers.Serializer):
    otp_id = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True, max_length=8)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = services.get_user_by_otp(
            validated_data["otp_id"], validated_data["code"]
        )
        return _issue_pair_for(user)


# -------- Password sign-up (customer only) --------
class PasswordSignUpSerializer(serializers.Serializer):
    mobile = serializers.RegexField(r"^09\d{9}$", max_length=11, write_only=True)
    password = serializers.CharField(
        write_only=True, min_length=6, trim_whitespace=False
    )
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = services.register_user_by_password(
            validated_data["mobile"], validated_data["password"]
        )
        return _issue_pair_for(user)


# -------- OTP sign-up (customer only) --------
class MobileSignUpStep1Serializer(serializers.Serializer):
    mobile = serializers.RegexField(r"^09\d{9}$", max_length=11, write_only=True)
    otp_id = serializers.CharField(read_only=True)

    def create(self, validated_data):
        otp = services.send_otp(validated_data["mobile"])
        return {"otp_id": str(otp.id)}


class SignUpStep2Serializer(serializers.Serializer):
    otp_id = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True, max_length=8)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = services.register_user_by_otp(
            validated_data["otp_id"], validated_data["code"]
        )
        return _issue_pair_for(user)


# -------- User read serializer --------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
