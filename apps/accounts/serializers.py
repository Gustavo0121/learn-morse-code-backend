"""Serializers do app accounts."""

from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Cadastro de usuário — a senha nunca aparece em respostas (write_only)."""

    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # Passa um usuário transiente para o UserAttributeSimilarityValidator
        # poder comparar a senha com username/email.
        transient_user = User(username=attrs.get("username", ""), email=attrs.get("email", ""))
        validate_password(attrs["password"], user=transient_user)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        # create_user aplica o hashing padrão do Django (set_password).
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """Leitura e atualização do perfil do usuário autenticado."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class CurrentPasswordSerializer(serializers.Serializer):
    """Base comum: confirma a identidade exigindo a senha atual."""

    current_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, value: str) -> str:
        user: User = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value


class ChangePasswordSerializer(CurrentPasswordSerializer):
    """Troca de senha — aplica os validators padrão e invalida sessões antigas."""

    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_new_password(self, value: str) -> str:
        validate_password(value, user=self.context["request"].user)
        return value

    def save(self, **kwargs: Any) -> None:
        user: User = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])


class DeleteAccountSerializer(CurrentPasswordSerializer):
    """Confirmação de exclusão de conta — exige a senha atual."""
