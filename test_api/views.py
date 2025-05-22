from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import inline_serializer, extend_schema, OpenApiParameter
from rest_framework import serializers
from rest_framework.views import APIView
from config.renderers import custom_response
from utils.test_utils import  simple_extend_schema


class HelloWorldDataSerializer(serializers.Serializer):
    id = serializers.CharField()


class HelloWorldView(APIView):
    # 序列化器声明data的schema
    # serializer_class = HelloWorldDataSerializer

    # @extend_schema(
    #     summary="示例接口",
    #     parameters=[
    #         OpenApiParameter(
    #             name="name",
    #             type=OpenApiTypes.STR,
    #             # location=OpenApiParameter.QUERY,
    #             required=True,
    #             description="用户名"
    #         ),
    #         OpenApiParameter(
    #             name="age",
    #             type=OpenApiTypes.INT,
    #             # location=OpenApiParameter.QUERY,
    #             required=False,
    #             description="年龄"
    #         ),
    #     ],
    #     responses={
    #         200: inline_serializer(
    #             name="MyCustomResponse",
    #             fields={
    #                 "custom_code": serializers.IntegerField(),
    #                 "msg": serializers.CharField(),
    #                 "payload": inline_serializer(
    #             name="My2CustomResponse",
    #             fields={
    #                 "custom_code": serializers.IntegerField(),
    #                 "msg": serializers.CharField(),
    #                 "payload": serializers.DictField()
    #             }
    #         )
    #             }
    #         )
    #     }
    # )
    @simple_extend_schema(
        summary="示例接口",
        parameters={
            "name": ("str", True, "用户名"),
            "age": ("int", False, "年龄"),
        },
        responses={
            200: {
                "msg": "str",
                "payload": {
                    "custom_code": "int",
                    "msg": "str",
                    "payload": "dict"
                }
            }
        }
    )
    def get(self, request):
        #返回数据要三段式符合要求
        return custom_response(data={"id":23},code=23)

    @simple_extend_schema(
        summary="完整示例：参数 + 请求体 + 响应体",

        parameters={
            "keyword": ("str", True, "搜索关键词", None, "人工智能"),
            "page": ("int", False, "分页页码", 1, 1),
            "page_size": ("int", False, "每页数量", 10, 10),
            "active": ("bool", False, "是否启用", True, True),
            "filter_date": ("date", False, "过滤日期", None, "2024-05-20"),
        },

        request_body={
            "name": ("str", True, "用户姓名", None, "张三"),
            "email": ("email", False, "邮箱地址", None, "zhangsan@example.com"),
            "birthdays": ("list[date]", False, "多个生日日期", None, ["2000-01-01", "2010-02-02"]),
            "tags": ("list[str]", False, "标签数组", None, ["AI", "前端", "大模型"]),
            "uuid_list": ("list[uuid]", False, "UUID数组", None, ["123e4567-e89b-12d3-a456-426614174000"]),
            "score": ("decimal", False, "考试分数", "98.5", "85.0"),
            "gender": ("str", True, "性别", None, "male", ["male", "female", "other"]),
            "nested_info": ({
                                "school": ("str", True, "学校名称", None, "清华大学"),
                                "grade": ("int", False, "年级", 3, 3),
                            }, True, "嵌套信息"),
        },

        responses={
            200: {
                "code": ("int", True, "状态码", 0, 0),
                "msg": ("str", True, "消息", "成功", "操作成功"),
                "data": {
                             "user_id": ("uuid", True, "用户ID", None, "123e4567-e89b-12d3-a456-426614174000"),
                             "created_at": ("datetime", True, "创建时间", None, "2025-05-22T14:00:00Z"),
                             "roles": ("list[str]", False, "角色列表", None, None),  # example置None，避免误判类型
                         },
            }
        }

    )
    def post(self, request):
        # 这里返回示例
        data = {
            "id": 1001,
            "username": request.data.get("username"),
            "roles": ["admin", "user"]
        }
        return custom_response(data=data, code=200)

