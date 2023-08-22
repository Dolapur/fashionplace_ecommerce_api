from django.contrib.auth import get_user_model
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



User = get_user_model()

def get_tokens_for_user(user: User):
    """
    Get JWT tokens for the given user.

    :param user: The user for whom to generate the tokens.
    :type user: User
    :return: Dictionary containing the access and refresh tokens.
    :rtype: dict
    """
    refresh = RefreshToken.for_user(user)

    tokens = {
        "access": str(refresh.access_token), 
        "refresh": str(refresh)
    }

    return tokens


class JWTCreateView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_summary="Create JWT token",
        operation_description="Create a new access token valid for a day and refesh token valid for two days by providing valid credentials.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access": openapi.Schema(type=openapi.TYPE_STRING),
                "refresh": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )},
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user is not None:
            tokens = get_tokens_for_user(user)
            response = {
                "tokens": tokens
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


class JWTRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="Refresh JWT token",
        operation_description="Refresh an existing JWT access token by passing in a refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )},
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            tokens = {
                "access": access_token,
                "refresh": refresh_token
            }
            return Response(data=tokens, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(data={"message": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class JWTVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        operation_summary="Verify JWT token",
        operation_description="Verify the validity of an existing JWT token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["token"],
            properties={
                "token": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )},
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        try:
            decoded_token = AccessToken(token)
        except Exception as e:
            return Response(data={"message": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(data={"message": "Token is valid"}, status=status.HTTP_200_OK)