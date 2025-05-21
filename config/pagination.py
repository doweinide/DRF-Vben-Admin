from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.conf import settings
#自定义配置返回字段
DEFAULT_PAGINATION_KEYS = {
    "count": "total",
    "next": "next_page",
    "previous": "prev_page",
    "results": "items",
}
class CustomPageNumberPagination(PageNumberPagination):
    # 自定义请求参数名
    page_query_param = 'page'            # 请求页码参数名，默认是 'page'
    page_size_query_param = 'page_size'    # 请求每页条数参数名，默认是 'page_size'
    max_page_size = 100
    page_size = 10

    def get_key(self, key):
        """从配置中取分页字段映射，没有就使用当前文件的DEFAULT_PAGINATION_KEYS"""
        keys = getattr(settings, 'CUSTOM_PAGINATION_KEYS', DEFAULT_PAGINATION_KEYS)
        return keys.get(key, key)  # 如果没配置，则保留原字段名

    def get_paginated_response(self, data):
        return Response({
            self.get_key("count"): self.page.paginator.count,
            self.get_key("next"): self.get_next_link(),
            self.get_key("previous"): self.get_previous_link(),
            self.get_key("results"): data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'required': [self.get_key("count"), self.get_key("results")],
            'properties': {
                self.get_key("count"): {
                    'type': 'integer',
                    'example': 123,
                },
                self.get_key("next"): {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': f'http://api.example.org/list/?{self.page_query_param}=4',
                },
                self.get_key("previous"): {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': f'http://api.example.org/list/?{self.page_query_param}=2',
                },
                self.get_key("results"): schema,
            },
        }