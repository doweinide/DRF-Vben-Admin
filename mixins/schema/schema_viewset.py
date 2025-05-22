"""
自动为 ModelViewSet 添加 API 文档的工具类

提供一个自动为 ModelViewSet 标准方法添加 extend_schema 装饰器的视图集基类，
减少手动编写重复的 API 文档代码。
"""

from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
import types
from functools import wraps
class SchemaModelViewSet(viewsets.ModelViewSet):
    """
    自动为 ModelViewSet 的标准方法添加 extend_schema 装饰器
    
    自动根据视图集的文档字符串或自定义的 schema_name 属性，为标准的 CRUD 方法
    添加合适的 API 摘要。继承此类可以大大减少文档注释的工作量。
    """
    
    # 标准操作的摘要模板
    schema_summary_mapping = {
        'list': '获取{name}列表',
        'retrieve': '获取单个{name}详情',
        'create': '创建{name}',
        'update': '更新{name}（整体更新）',
        'partial_update': '部分更新{name}',
        'destroy': '删除{name}'
    }
    
    # 这个属性用于在 summary 中显示的名称
    schema_name = ""
    
    def __new__(cls, *args, **kwargs):
        """创建实例时应用装饰器"""
        instance = super().__new__(cls)

        # 装饰子类的方法
        cls._apply_schema_decorators(cls)
        
        return instance
    
    @classmethod
    def _apply_schema_decorators(cls, subclass):
        """
        为子类的方法应用装饰器
        
        参数:
            subclass: 要应用装饰器的子类
        """
        # 获取 schema_name
        name = subclass.schema_name
        if not name and subclass.__doc__:
            try:
                name = subclass.__doc__.split('视图集')[0].strip()
            except:
                name = subclass.__doc__.strip()
        if not name:
            name = "对象"
        
        # 为每个方法添加装饰器
        for method_name, summary_template in cls.schema_summary_mapping.items():
            if hasattr(subclass, method_name) and callable(getattr(subclass, method_name)):
                method_func = getattr(subclass, method_name)
                
                # 检查方法是否已有装饰器
                if not hasattr(method_func, '_spectacular_annotation'):
                    # 格式化 summary
                    summary = summary_template.format(name=name)
                    
                    # 使用 extend_schema 装饰方法
                    decorated_method = extend_schema(summary=summary)(method_func)
                    
                    # 设置回子类
                    setattr(subclass, method_name, decorated_method)
    


# 预先为每个方法创建并应用装饰器
def _apply_schema_decorators():
    """为 SchemaModelViewSet 的标准方法添加 extend_schema 装饰器"""


    for method_name, summary_template in SchemaModelViewSet.schema_summary_mapping.items():
        if hasattr(SchemaModelViewSet, method_name):
            original_method = getattr(viewsets.ModelViewSet, method_name)

            # 创建装饰器
            decorated_method = extend_schema(
                summary=summary_template.format(name='')
            )(original_method)

            # 保留原始方法的属性
            # 加上 wraps 保留元信息
            decorated_method = wraps(original_method)(decorated_method)
            # 设置到 SchemaModelViewSet 类
            setattr(SchemaModelViewSet, method_name, decorated_method)

# 应用装饰器
_apply_schema_decorators()



