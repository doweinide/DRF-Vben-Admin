from rest_framework import serializers
from .models import User, Role, Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all()
    )

    class Meta:
        model = User
        # fields = "__all__"
        exclude =["user_permissions","groups"]
