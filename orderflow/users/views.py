from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from orderflow.contrib.views import regular_post_action

from . import serializers

User = get_user_model()


class AuthenticationViewSetV1(ViewSet):
    permission_classes = [AllowAny]
    throttle_scope = "authentication"

    def get_serializer_class(self):
        mapping = {
            "refresh_token": serializers.TokenRefreshSerializer,
            "sign_in_password": serializers.PasswordSignInSerializer,
            "sign_up_password": serializers.PasswordSignUpSerializer,
            "sign_in_mobile_step1": serializers.MobileSignInStep1Serializer,
            "sign_in_otp_step2": serializers.SignInStep2Serializer,
            "sign_up_mobile_step1": serializers.MobileSignUpStep1Serializer,
            "sign_up_otp_step2": serializers.SignUpStep2Serializer,
        }
        return mapping[self.action]

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }
        return self.get_serializer_class()(*args, **kwargs)

    @action(detail=False, methods=["post"], url_path="refresh-jwt")
    def refresh_token(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    # Mobile/Password sign-in
    @action(detail=False, methods=["post"], url_path="sign-in/password")
    @regular_post_action
    def sign_in_password(self, request):
        pass

    # Mobile/Password sign-up (customer only)
    @action(detail=False, methods=["post"], url_path="sign-up/password")
    @regular_post_action
    def sign_up_password(self, request):
        pass

    # OTP sign-in (2-step)
    @action(detail=False, methods=["post"], url_path="sign-in/mobile/step1")
    @regular_post_action
    def sign_in_mobile_step1(self, request):
        pass

    @action(detail=False, methods=["post"], url_path="sign-in/otp/step2")
    @regular_post_action
    def sign_in_otp_step2(self, request):
        pass

    # OTP sign-up (2-step, customer only)
    @action(detail=False, methods=["post"], url_path="sign-up/mobile/step1")
    @regular_post_action
    def sign_up_mobile_step1(self, request):
        pass

    @action(detail=False, methods=["post"], url_path="sign-up/otp/step2")
    @regular_post_action
    def sign_up_otp_step2(self, request):
        pass


class UserViewSetV1(RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated,)
    throttle_scope = "users"
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):
        return User.objects.all()

    def get_serializer_class(self):
        return serializers.UserSerializer

    @action(detail=False, methods=["get"], url_path=r"i")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
