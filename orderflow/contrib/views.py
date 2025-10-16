from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def regular_post_action(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        self = args[0]
        request = args[1]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return func_wrapper


def regular_detailed_post_action(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        self = args[0]
        request = args[1]
        obj = self.get_object()
        serializer = self.get_serializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return func_wrapper
