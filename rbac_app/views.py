from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.pagination import CustomPageNumberPagination
from .models import User, Role, Permission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    @action(detail=False, methods=["get"], url_path="active-users")
    def active_users(self, request):
        """
        获取活跃用户列表（示例接口）
        """
        # 创建分页器
        paginator = CustomPageNumberPagination()
        paginator.page_size=1
        active_users = self.queryset.filter(is_active=True)
        page = paginator.paginate_queryset(active_users,request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
