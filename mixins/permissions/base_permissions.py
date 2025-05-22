from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限，只允许对象的所有者编辑它
    其他用户只能查看
    
    要求模型有owner字段或user字段，指向用户模型
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        # 所以我们始终允许GET, HEAD 或 OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 写入权限只允许给对象的所有者
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限，只允许管理员进行写操作
    其他用户只能查看
    """
    def has_permission(self, request, view):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 写入权限只允许给管理员
        return request.user and request.user.is_staff


class IsOwnerOrStaff(permissions.BasePermission):
    """
    自定义权限，只允许对象的所有者或管理员编辑它
    """
    def has_object_permission(self, request, view, obj):
        # 管理员始终有权限
        if request.user and request.user.is_staff:
            return True
            
        # 检查是否是对象所有者
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    自定义权限，要求用户既已认证又是活跃状态
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active 