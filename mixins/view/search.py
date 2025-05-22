"""
搜索相关的 ModelViewSet Mixins

提供支持搜索功能的 ModelViewSet 混入类，可简化基于查询参数的搜索功能实现。
"""

from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from drf_spectacular.utils import extend_schema, OpenApiParameter

class SearchableListModelMixin(viewsets.ModelViewSet):
    """
    基础搜索功能混入类

    为 ModelViewSet 提供基本的搜索功能，支持对序列化器中定义的字段进行模糊查询。
    默认使用 icontains 查询方式（不区分大小写的包含查询）。
    
    使用方法:
    ```python
    class MyViewSet(SearchableListModelMixin, viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MyModelSerializer
    ```
    """
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='field_name', description='按字段名搜索（替换为实际字段名）', required=False, type=str)
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        列表查询，支持按参数搜索

        根据请求参数自动构建查询条件，支持对序列化器中的字段进行搜索。
        """
        # 获取查询参数
        query_params = request.query_params
        # 获取序列化器的字段
        serializer_fields = set(self.get_serializer().fields.keys())

        # 构建查询集
        query = Q()
        for field, value in query_params.items():
            # 检查字段是否在序列化器中
            if field in serializer_fields and value:
                # 对符合条件的字段进行模糊查询
                query.add(Q(**{f'{field}__icontains': value}), Q.AND)

        # 应用查询集到模型上
        queryset = self.get_queryset().filter(query)
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 序列化查询结果
        serializer = self.get_serializer(queryset, many=True)

        # 返回响应
        return Response(serializer.data, status=status.HTTP_200_OK)


class SearchableListModelMixinUp(viewsets.ModelViewSet):
    """
    高级搜索功能混入类
    
    扩展了基础搜索功能，增加了对时间范围的支持。
    使用者需要通过 time_range_fields 属性指定哪些字段支持时间范围查询。
    
    使用方法:
    ```python
    class MyViewSet(SearchableListModelMixinUp, viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MyModelSerializer
        time_range_fields = ['created_at', 'updated_at']  # 指定支持时间范围查询的字段
    ```
    
    前端使用示例:
    GET /api/mymodel/?name=test&created_at[]=2022-01-01T00:00:00&created_at[]=2022-12-31T23:59:59
    """
    # 默认为空列表，子类需要重写该属性以指定支持时间范围查询的字段
    time_range_fields = []

    @extend_schema(
        parameters=[
            OpenApiParameter(name='field_name', description='按字段名搜索（替换为实际字段名）', required=False, type=str),
            OpenApiParameter(name='time_field[]', description='时间范围查询（替换为实际时间字段名，需要两个值表示开始和结束时间）', 
                           required=False, type=str, many=True)
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        列表查询，支持按参数搜索和时间范围过滤
        
        除了基本的字段搜索外，还支持对指定的时间字段进行范围查询。
        时间范围需要提供开始和结束时间，格式为 ISO 8601（如：2022-01-01T00:00:00）。
        """
        query_params = request.query_params
        serializer_fields = set(self.get_serializer().fields.keys())
        query = Q()

        # 普通字段模糊搜索（排除时间范围字段）
        for field, value in query_params.items():
            if field in serializer_fields and field not in self.time_range_fields and value:
                query.add(Q(**{f'{field}__icontains': value}), Q.AND)

        # 时间范围过滤
        for time_field in self.time_range_fields:
            time_values = query_params.getlist(f'{time_field}[]')
            if time_values and len(time_values) == 2:
                start_date = parse_datetime(time_values[0])
                end_date = parse_datetime(time_values[1])
                if start_date and end_date:
                    # 确保时间带有时区信息
                    start_date = make_aware(start_date) if start_date.tzinfo is None else start_date
                    end_date = make_aware(end_date) if end_date.tzinfo is None else end_date
                    query.add(Q(**{f'{time_field}__range': (start_date, end_date)}), Q.AND)

        # 查询和排序
        queryset = self.get_queryset().filter(query).order_by('id')  # 默认按 ID 排序
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 