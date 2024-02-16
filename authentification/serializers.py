from wsgiref import validate
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers, status
from rest_framework import validators
from rest_framework.fields import (
    EmailValidator,
    MaxLengthValidator,
    MinLengthValidator,
    SerializerMethodField,
)
from rest_framework.validators import UniqueValidator

from authentification.models import User
from formations.models import Formation
from formations.serializers import FormationSerializer


class UserSerializer(serializers.ModelSerializer):
    validated_at = serializers.DateField(required=False)
    password = serializers.CharField(required=True, write_only=True)
    confirmpassword = serializers.CharField(required=True, write_only=True)
    titre = serializers.CharField(required=True)
    # type = serializers.ChoiceField(choices=["etudiant", "enseignant"])
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.values("email")),
            EmailValidator(),
        ]
    )
    nom = serializers.CharField(required=True, validators=[MaxLengthValidator(20)])
    prenom = serializers.CharField(required=True, validators=[MaxLengthValidator(20)])

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def validate_titre(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("Titre invalid.")
        return value

    def validate(self, data):
        if data.get("password") != data.get("confirmpassword"):
            raise serializers.ValidationError(
                {"confirmnewpassword": "Value isnt the same as password."}
            )

        return data

    def create(self, validated_data):
        validated_data.pop("confirmpassword", None)
        validated_data["type"] = "etudiant"
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)

    formation = SerializerMethodField()

    def get_formation(self, user):
        if user.inscrit_a:
            return FormationSerializer(user.inscrit_a).data
        return None

    pfp = serializers.SerializerMethodField(required=False)

    def get_pfp(self, obj):
        if obj.pfp:
            return self.context["request"].build_absolute_uri(obj.pfp.url)
        return None

    ma_formation = SerializerMethodField()

    def get_ma_formation(self, user):
        try:
            formation = Formation.objects.get(responsable=user)
        except Formation.DoesNotExist:
            return None
        serializer = FormationSerializer(formation)
        return serializer.data

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "password",
            "validated_at",
            "confirmpassword",
            "titre",
            "type",
            "naissance",
            "nom",
            "prenom",
            "pfp",
            "formation",
            "ma_formation",
        ]


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pfp"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "password",
            "confirmnewpassword",
            "newpassword",
            "titre",
            "type",
            "naissance",
            "nom",
            "prenom",
            "pfp",
        ]

    id = serializers.IntegerField(required=False)
    pfp = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)
    newpassword = serializers.CharField(required=False)
    confirmnewpassword = serializers.CharField(required=False)
    titre = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=["etudiant", "enseignant"])
    email = serializers.CharField(
        validators=[
            EmailValidator(),
        ]
    )
    nom = serializers.CharField(required=True, validators=[MaxLengthValidator(20)])
    prenom = serializers.CharField(required=True, validators=[MaxLengthValidator(20)])

    def validate(self, data):
        if data.get("newpassword") != data.get("confirmnewpassword"):
            raise serializers.ValidationError(
                {"confirmnewpassword": "Value isnt the same as password."}
            )

        return data

    def validate_password(self, value):
        user = self.instance
        if not check_password(value, user.password):
            raise serializers.ValidationError("Current password is incorrect.")
        return make_password(value)

    def validate_email(self, value):
        user = self.instance

        if user.email == value:
            return value

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already used.")

        return value

    def update(self, instance, validated_data):
        instance.__dict__.update(**validated_data)
        if "newpassword" in validated_data:
            validated_data["password"] = make_password(validated_data["newpassword"])
        else:
            validated_data["password"] = instance.password
        return super().update(instance, validated_data)
