"""
Schema 相关工具

包含 DRF Spectacular API 文档生成的简化工具。
"""

from .schema_utils import simple_extend_schema
from .schema_viewset import SchemaModelViewSet

__all__ = ['SchemaModelViewSet', 'simple_extend_schema']