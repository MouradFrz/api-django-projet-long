from functools import partial
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.db.migrations import serializer
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from yaml import serialize
from authentification.models import User
from authentification.serializers import (
    ProfilePictureSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .permission import IsEnseignant, IsEtudiant, IsInactive
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
import jwt

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@authentication_classes([])
def login(request):
    data = request.data
    response = Response()
    email = data.get("email", None)
    password = data.get("password", None)
    user = authenticate(email=email, password=password)

    if user is not None:
        data = get_tokens_for_user(user)
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=data["access"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        response.set_cookie(
            key=settings.SIMPLE_JWT["REFRESH_COOKIE"],
            value=data["refresh"],
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        csrf.get_token(request)
        response.data = {"Success": "Login successfully", "data": data}
        return response
    else:
        return Response(
            {"Invalid": "Invalid username or password"},
            status=status.HTTP_404_NOT_FOUND,
        )


def get_access_for_refresh(token):
    refresh_token = RefreshToken(token)
    accesstoken = refresh_token.access_token
    return str(accesstoken)


@api_view(["POST"])
@authentication_classes([])
def refresh(request):
    try:
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["REFRESH_COOKIE"])
        if not refresh_token:
            return Response(
                {"Invalid": "Refresh token not found."},
                status=status.HTTP_403_FORBIDDEN,
            )
        access = get_access_for_refresh(refresh_token)
    except TokenError:
        return Response(
            {"Invalid": "Refresh token is invalid or expired."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    decoded = jwt.decode(access, settings.SECRET_KEY, algorithms=["HS256"])
    userid = decoded.get("user_id")
    user = User.objects.get(id=userid)
    data = get_tokens_for_user(user)
    response = Response()
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=data["access"],
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )
    response.set_cookie(
        key=settings.SIMPLE_JWT["REFRESH_COOKIE"],
        value=data["refresh"],
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"type": request.user.type})


@api_view(["POST"])
@authentication_classes([])
def logout(request):
    response = Response()
    response.delete_cookie(key=settings.SIMPLE_JWT["AUTH_COOKIE"])
    response.delete_cookie(key=settings.SIMPLE_JWT["REFRESH_COOKIE"])
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_verification_link(request):
    confirmation_token = default_token_generator.make_token(request.user)
    uidb64 = urlsafe_base64_encode(force_bytes(request.user.id))
    if request.user.validated_at:
        return Response(
            "You account is already activated.", status=status.HTTP_403_FORBIDDEN
        )
    confirmation_link = (
        f"http://localhost:8000/auth/validate-email/{uidb64}/{confirmation_token}"
    )
    html_message = render_to_string(
        "email.html", {"confirmation_link": confirmation_link}
    )
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="Your email validation",
        body=plain_message,
        from_email="projet-long@no-rep.fr",
        to=[request.user.email],
    )

    message.attach_alternative(html_message, "text/html")
    message.send()

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def validate_email(request, id, confirmation_token):
    try:
        user_id = urlsafe_base64_decode(id).decode()
        user = User.objects.get(id=user_id)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is None:
        return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
    if not default_token_generator.check_token(user, confirmation_token):
        return Response(
            "Token is invalid or expired. Please request another confirmation email by signing in.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if user.validated_at:
        return Response(
            "You account is already activated.", status=status.HTTP_403_FORBIDDEN
        )
    user.validated_at = now()
    user.save()
    return render(request, "success.html")


@api_view(["POST"])
def create(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = User.objects.filter(id=request.user.id).first()
    if user:
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)
    else:
        return Response({"message": "User not found"}, status=404)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_pfp(request):
    serializer = ProfilePictureSerializer(request.user, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update(request):
    instance = User.objects.get(id=request.user.id)
    serializer = UserUpdateSerializer(
        data={**request.data, "password": request.data["password"]},
        instance=instance,
        partial=True,
    )
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def get_reset(request):
    try:
        user = User.objects.get(email=request.data["email"])
    except:
        return Response("Your email is incorrect.", status=status.HTTP_404_NOT_FOUND)

    token = default_token_generator.make_token(user)

    uid = urlsafe_base64_encode(force_bytes(user.id))
    reset_url = f"http://localhost:8000/auth/password/reset/{uid}/{token}"

    html_message = render_to_string("password_reset.html", {"reset_link": reset_url})
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject="Your password reset",
        body=plain_message,
        from_email="projet-long@no-rep.fr",
        to=[user.email],
    )

    message.attach_alternative(html_message, "text/html")
    message.send()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
def reset_password(request, uid, token):
    user_id = urlsafe_base64_decode(uid).decode()
    user = User.objects.get(id=user_id)

    if user is None:
        return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
    if not default_token_generator.check_token(user, token):
        return Response(
            "Token is invalid or expired. Please request another confirmation email by signing in.",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if request.method == "POST":
        if not request.data["password"] or not request.data["confirmpassword"]:
            return Response(
                {"error": "You have to provide a password and a confirmation."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data["password"] != request.data["confirmpassword"]:
            return Response(
                {"error": "Passwords don't match."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.password = make_password(request.data["password"])
        user.save()
        # return Response(status=status.HTTP_200_OK) return a success page
        return render(request, "success.html")
    else:
        return render(request, "reset-password.html", {"uid": uid, "token": token})
        # Return a page with the token and UID that has a form who calls this ting with POST
    # default_token_generator.make_token(user)
