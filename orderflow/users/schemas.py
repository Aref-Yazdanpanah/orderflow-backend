from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers as drf_serializers

from . import serializers as user_serializers

# ------------------------------------------------------------------------------
# Shared docs bits
# ------------------------------------------------------------------------------


class APIErrorSerializer(drf_serializers.Serializer):
    """
    Matches the project's error handler shape: {"detail": [<str>, ...], "code": "<str>"}
    """

    detail = drf_serializers.ListField(child=drf_serializers.CharField())
    code = drf_serializers.CharField()


class TokenPairOutSerializer(drf_serializers.Serializer):
    """
    Generic JWT response for SimpleJWT flows. Both `access` and `refresh` are returned.
    """

    access = drf_serializers.CharField()
    refresh = drf_serializers.CharField()


class OTPIdOutSerializer(drf_serializers.Serializer):
    """Response shape for OTP step1 endpoints."""

    otp_id = drf_serializers.CharField()


# ------------------------------------------------------------------------------
# Examples – Auth (local mobile format 09XXXXXXXXX)
# ------------------------------------------------------------------------------

EXAMPLE_PASSWORD_SIGNIN_REQ = OpenApiExample(
    name="Password Sign-In (request)",
    value={"mobile": "09123456789", "password": "S3cret!"},
    request_only=True,
)

EXAMPLE_PASSWORD_SIGNIN_RES = OpenApiExample(
    name="Password Sign-In (response)",
    value={"access": "<jwt-access>", "refresh": "<jwt-refresh>"},
    response_only=True,
)

EXAMPLE_PASSWORD_SIGNUP_REQ = OpenApiExample(
    name="Password Sign-Up (request)",
    value={"mobile": "09123456789", "password": "S3cret!"},
    request_only=True,
)

EXAMPLE_PASSWORD_SIGNUP_RES = OpenApiExample(
    name="Password Sign-Up (response)",
    value={"access": "<jwt-access>", "refresh": "<jwt-refresh>"},
    response_only=True,
)

EXAMPLE_REFRESH_REQ = OpenApiExample(
    name="Refresh (request)",
    value={"refresh": "<jwt-refresh>"},
    request_only=True,
)

EXAMPLE_TOKEN_PAIR_RES = OpenApiExample(
    name="JWT Pair (response)",
    value={"access": "<jwt-access>", "refresh": "<jwt-refresh>"},
    response_only=True,
)

EXAMPLE_SIGNIN_STEP1_REQ = OpenApiExample(
    name="Sign-In Step 1 (request)",
    value={"mobile": "09123456789"},
    request_only=True,
)

EXAMPLE_SIGNIN_STEP1_RES = OpenApiExample(
    name="Sign-In Step 1 (response)",
    value={"otp_id": "2c9f7b36-2d2e-4a06-8e59-59c8f78a2d5e"},
    response_only=True,
)

EXAMPLE_SIGNIN_STEP2_REQ = OpenApiExample(
    name="Sign-In Step 2 (request)",
    value={"otp_id": "2c9f7b36-2d2e-4a06-8e59-59c8f78a2d5e", "code": "12345"},
    request_only=True,
)

EXAMPLE_SIGNUP_STEP1_REQ = OpenApiExample(
    name="Sign-Up Step 1 (request)",
    value={"mobile": "09123456789"},
    request_only=True,
)

EXAMPLE_SIGNUP_STEP1_RES = OpenApiExample(
    name="Sign-Up Step 1 (response)",
    value={"otp_id": "f8a5a2c4-8db6-4b2c-9b1a-0a6e0b8f3f5a"},
    response_only=True,
)

EXAMPLE_SIGNUP_STEP2_REQ = OpenApiExample(
    name="Sign-Up Step 2 (request)",
    value={"otp_id": "f8a5a2c4-8db6-4b2c-9b1a-0a6e0b8f3f5a", "code": "12345"},
    request_only=True,
)

# ------------------------------------------------------------------------------
# Examples – Users
# ------------------------------------------------------------------------------

EXAMPLE_ME_RES = OpenApiExample(
    name="Me (response)",
    value={
        "id": "7f33c9d4-3bc0-40e4-97b7-f7294dd6de31",
        "username": "09123456789",
        "first_name": "Alice",
        "last_name": "Smith",
        "is_superuser": False,
        "date_joined": "2025-09-10T12:45:00Z",
        "last_login": "2025-09-10T13:20:00Z",
    },
    response_only=True,
)

# ------------------------------------------------------------------------------
# Tags
# ------------------------------------------------------------------------------

TAGS_AUTH = ["Auth"]
TAGS_USERS = ["Users"]

# ------------------------------------------------------------------------------
# Auth – endpoint schemas
# ------------------------------------------------------------------------------

refresh_token_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_refresh_jwt",
    summary="Refresh JWT access token",
    description=(
        "Exchange a valid **refresh** token for a new **access** token. "
        "This project issues both `access` and `refresh` in responses."
    ),
    request=user_serializers.TokenRefreshSerializer,
    responses={200: TokenPairOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_REFRESH_REQ, EXAMPLE_TOKEN_PAIR_RES],
)

password_sign_in_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_in_password",
    summary="Sign-In with mobile + password",
    description=(
        "Authenticate using local mobile format (`^09\\d{9}$`) and a password. "
        "On success, returns a JWT `access` and `refresh`."
    ),
    request=user_serializers.PasswordSignInSerializer,
    responses={200: TokenPairOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_PASSWORD_SIGNIN_REQ, EXAMPLE_PASSWORD_SIGNIN_RES],
)

password_sign_up_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_up_password",
    summary="Sign-Up with mobile + password (customer)",
    description=(
        "Register a **customer** account using local mobile format (`^09\\d{9}$`) "
        "and a password (min length 6). Returns a JWT `access` and `refresh`."
    ),
    request=user_serializers.PasswordSignUpSerializer,
    responses={200: TokenPairOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_PASSWORD_SIGNUP_REQ, EXAMPLE_PASSWORD_SIGNUP_RES],
)

sign_in_mobile_step1_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_in_mobile_step1",
    summary="Sign-In Step 1 (request OTP)",
    description=(
        "Start the **sign-in** flow using a local mobile number (`^09\\d{9}$`). "
        "If the user exists, an OTP is sent and a real `otp_id` is returned. "
        "If the user does **not** exist, a random `otp_id` is returned to prevent enumeration."
    ),
    request=user_serializers.MobileSignInStep1Serializer,
    responses={200: OTPIdOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_SIGNIN_STEP1_REQ, EXAMPLE_SIGNIN_STEP1_RES],
)

sign_in_otp_step2_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_in_otp_step2",
    summary="Sign-In Step 2 (verify OTP and issue tokens)",
    description=(
        "Complete **sign-in** by verifying the `otp_id` and `code`. "
        "On success, returns a JWT `access` and `refresh`."
    ),
    request=user_serializers.SignInStep2Serializer,
    responses={200: TokenPairOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_SIGNIN_STEP2_REQ, EXAMPLE_TOKEN_PAIR_RES],
)

sign_up_mobile_step1_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_up_mobile_step1",
    summary="Sign-Up Step 1 (request OTP)",
    description=(
        "Start the **sign-up** flow using a local mobile number (`^09\\d{9}$`). "
        "Always returns a real `otp_id` and sends the OTP to the provided number."
    ),
    request=user_serializers.MobileSignUpStep1Serializer,
    responses={200: OTPIdOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_SIGNUP_STEP1_REQ, EXAMPLE_SIGNUP_STEP1_RES],
)

sign_up_otp_step2_schema = extend_schema(
    tags=TAGS_AUTH,
    operation_id="auth_sign_up_otp_step2",
    summary="Sign-Up Step 2 (verify OTP and create account)",
    description=(
        "Complete **sign-up** by verifying the `otp_id` and `code`. "
        "Creates the user if needed and returns a JWT `access` and `refresh`."
    ),
    request=user_serializers.SignUpStep2Serializer,
    responses={200: TokenPairOutSerializer, 400: APIErrorSerializer},
    examples=[EXAMPLE_SIGNUP_STEP2_REQ, EXAMPLE_TOKEN_PAIR_RES],
)

# ------------------------------------------------------------------------------
# Users – endpoint schemas
# ------------------------------------------------------------------------------

me_schema = extend_schema(
    tags=TAGS_USERS,
    operation_id="users_me_retrieve",
    summary="Get current user",
    description="Return the authenticated user's `User` object.",
    request=None,
    responses={200: user_serializers.UserSerializer, 401: APIErrorSerializer},
    examples=[EXAMPLE_ME_RES],
)
