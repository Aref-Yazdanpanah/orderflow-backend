from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def error_handler(exception, context):
    if isinstance(exception, DjangoValidationError):
        return Response(
            {
                "detail": exception.messages,
                "code": exception.code,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return drf_exception_handler(exception, context)
