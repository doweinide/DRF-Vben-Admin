from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField

# 权限类型
PERMISSION_TYPE_CHOICES = [
    ("catalog", "目录"),
    ("menu", "菜单"),
    ("button", "按钮"),
    ("iframe", "内嵌"),
    ("link", "外链"),
]

class Permission(models.Model):
    name = models.CharField(max_length=100, verbose_name="权限名称")
    code = models.CharField(max_length=100, unique=True, verbose_name="权限编码")
    type = models.CharField(max_length=20, choices=PERMISSION_TYPE_CHOICES)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    path = models.CharField(max_length=200, blank=True, null=True, help_text="前端路由地址")
    config = JSONField(default=dict, blank=True, null=True, help_text="其他配置信息")




class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'permission')


class User(AbstractUser):
    # 去掉 ManyToManyField
    pass


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')
