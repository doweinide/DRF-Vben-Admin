import uuid
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes
from rest_framework import serializers


# ---------- 类型映射 ----------
# 用于将自定义的字符串类型映射为 drf_spectacular 中对应的 OpenApiTypes 类型，方便自动生成文档时使用
type_mapping = {
    "str": OpenApiTypes.STR,
    "int": OpenApiTypes.INT,
    "bool": OpenApiTypes.BOOL,
    "float": OpenApiTypes.FLOAT,
    "list": OpenApiTypes.OBJECT,
    "dict": OpenApiTypes.OBJECT,
    "date": OpenApiTypes.DATE,
    "datetime": OpenApiTypes.DATETIME,
    "uuid": OpenApiTypes.UUID,
    "email": OpenApiTypes.STR,
    "decimal": OpenApiTypes.NUMBER,
}

# ---------- 字段映射 ----------
# 用于将字符串类型映射为对应的 DRF 序列化器字段类
field_mapping = {
    "str": serializers.CharField,
    "int": serializers.IntegerField,
    "bool": serializers.BooleanField,
    "float": serializers.FloatField,
    "dict": serializers.DictField,
    "list": serializers.ListField,
    "date": serializers.DateField,
    "datetime": serializers.DateTimeField,
    "uuid": serializers.UUIDField,
    "email": serializers.EmailField,
    "decimal": lambda **kwargs: serializers.DecimalField(max_digits=10, decimal_places=2, **kwargs),
}


# ---------- 字段构造工具 ----------
def build_serializer_field(cls_factory, required, help_text, default=None):
    """
    根据字段的参数构造序列化字段实例

    Args:
        cls_factory: 字段的序列化器类或工厂函数
        required: 是否必填
        help_text: 字段描述
        default: 默认值（如果有，则字段不再必填）

    Returns:
        具体的字段实例
    """
    kwargs = {"required": required, "help_text": help_text}
    if default is not None:
        kwargs["required"] = False  # 有默认值时，字段非必填
        kwargs["default"] = default
    return cls_factory(**kwargs)


# ---------- 类型解析工具 ----------
def get_field_class(type_str, enum=None):
    """
    解析字段类型字符串，返回对应的序列化器字段类或工厂函数
    支持 list 嵌套类型及枚举（ChoiceField）

    Args:
        type_str: 类型字符串，如 'str', 'list[int]'
        enum: 枚举选项列表（如存在，则使用 ChoiceField）

    Returns:
        序列化器字段类或工厂函数
    """
    # 处理 list 类型，如 list[int]
    if type_str.startswith("list[") and type_str.endswith("]"):
        inner_type = type_str[5:-1]
        child_cls = get_field_class(inner_type)
        return lambda **kwargs: serializers.ListField(child=child_cls(), **kwargs)

    # 处理枚举
    if enum:
        return lambda **kwargs: serializers.ChoiceField(choices=enum, **kwargs)

    # 普通类型映射
    field_cls = field_mapping.get(type_str)
    if callable(field_cls):
        return field_cls
    elif field_cls:
        return lambda **kwargs: field_cls(**kwargs)
    else:
        # 默认使用字符串字段
        return lambda **kwargs: serializers.CharField(**kwargs)


# ---------- 字段构造核心 ----------
def create_fields(field_dict):
    """
    根据字段定义字典递归构造 DRF 序列化器字段

    Args:
        field_dict: 字段定义字典，格式支持多种：
            - value 是元组，格式 (type, required, desc, default, example, enum)
            - value 是嵌套字典，表示嵌套序列化器
            - value 是简单类型字符串，表示字段类型

    Returns:
        dict: key 为字段名，value 为对应序列化器字段实例或 inline_serializer
    """
    fields = {}
    for key, val in field_dict.items():
        if isinstance(val, tuple):
            # 补全元组，确保长度为6，方便解包
            t = list(val) + [None] * (6 - len(val))
            type_str, required, desc, default, example, enum = t[:6]

            # 确保类型是字符串
            if not isinstance(type_str, str):
                type_str = "str"
            required = bool(required) if required is not None else False
            desc = desc or ""

            # 如果 type_str 是字典，则表示嵌套结构，递归创建内嵌序列化器
            if isinstance(type_str, dict):
                nested_name = f"{key.capitalize()}Nested_{uuid.uuid4().hex[:6]}"
                # 有默认值时，字段不必填
                real_required = required if default is None else False
                fields[key] = inline_serializer(
                    name=nested_name,
                    fields=create_fields(type_str),
                    required=real_required,
                    help_text=desc,
                    default=default,
                )
            else:
                # 普通字段，调用类型解析获取字段类
                serializer_cls = get_field_class(type_str, enum)
                help_text = desc
                # 追加示例说明
                if example is not None:
                    help_text += f" 示例: {example}"

                fields[key] = build_serializer_field(
                    serializer_cls,
                    required,
                    help_text,
                    default
                )

        elif isinstance(val, dict):
            # 字段值是字典，直接递归嵌套序列化器
            nested_name = f"{key.capitalize()}Nested_{uuid.uuid4().hex[:6]}"
            fields[key] = inline_serializer(
                name=nested_name,
                fields=create_fields(val),
            )
        else:
            # 简单类型字符串，直接映射字段
            field_cls = field_mapping.get(val, serializers.CharField)
            fields[key] = field_cls() if not callable(field_cls) else field_cls()
    return fields


# ---------- 主入口函数 ----------
def simple_extend_schema(summary="", parameters=None, responses=None, request_body=None):
    """
    生成 DRF-Spectacular 的 extend_schema 装饰器，用于快速定义接口文档

    Args:
        summary: 接口描述
        parameters: 请求参数字典，格式为 {参数名: (类型, 是否必填, 描述, 默认值, 示例, 枚举)}
        responses: 响应体字典，格式为 {状态码: 字段定义字典}
        request_body: 请求体字段定义字典

    Returns:
        drf_spectacular.utils.extend_schema 装饰器实例
    """
    param_list = []
    if parameters:
        for name, val in parameters.items():
            t = list(val) + [None] * (6 - len(val))
            type_str, required, desc, default, example, enum = t[:6]
            if not isinstance(type_str, str):
                type_str = "str"
            required = bool(required) if required is not None else False
            desc = desc or ""
            # 根据参数类型获取 OpenApiTypes 类型
            param_type = type_mapping.get(type_str.split("[")[0], OpenApiTypes.STR)
            param_list.append(
                OpenApiParameter(
                    name=name,
                    type=param_type,
                    required=required,
                    description=desc,
                )
            )

    resp_dict = {}
    if responses:
        # 遍历响应码及响应体结构，动态生成 inline_serializer
        for code, schema in responses.items():
            name = f"Resp{code}_{uuid.uuid4().hex[:6]}"
            resp_dict[code] = inline_serializer(name=name, fields=create_fields(schema))

    request_serializer = None
    if request_body:
        # 请求体也用 inline_serializer 封装
        name = f"Req_{uuid.uuid4().hex[:6]}"
        request_serializer = inline_serializer(name=name, fields=create_fields(request_body))

    return extend_schema(
        summary=summary,
        parameters=param_list,
        request=request_serializer,
        responses=resp_dict,
    )

# ----------示例---------
#     @simple_extend_schema(
#         summary="完整示例：参数 + 请求体 + 响应体",
#
#         parameters={
#             "keyword": ("str", True, "搜索关键词", None, "人工智能"),
#             "page": ("int", False, "分页页码", 1, 1),
#             "page_size": ("int", False, "每页数量", 10, 10),
#             "active": ("bool", False, "是否启用", True, True),
#             "filter_date": ("date", False, "过滤日期", None, "2024-05-20"),
#         },
#
#         request_body={
#             "name": ("str", True, "用户姓名", None, "张三"),
#             "email": ("email", False, "邮箱地址", None, "zhangsan@example.com"),
#             "birthdays": ("list[date]", False, "多个生日日期", None, ["2000-01-01", "2010-02-02"]),
#             "tags": ("list[str]", False, "标签数组", None, ["AI", "前端", "大模型"]),
#             "uuid_list": ("list[uuid]", False, "UUID数组", None, ["123e4567-e89b-12d3-a456-426614174000"]),
#             "score": ("decimal", False, "考试分数", "98.5", "85.0"),
#             "gender": ("str", True, "性别", None, "male", ["male", "female", "other"]),
#             "nested_info": ({
#                                 "school": ("str", True, "学校名称", None, "清华大学"),
#                                 "grade": ("int", False, "年级", 3, 3),
#                             }, True, "嵌套信息"),
#         },
#
#         responses={
#             200: {
#                 "code": ("int", True, "状态码", 0, 0),
#                 "msg": ("str", True, "消息", "成功", "操作成功"),
#                 "data": {
#                              "user_id": ("uuid", True, "用户ID", None, "123e4567-e89b-12d3-a456-426614174000"),
#                              "created_at": ("datetime", True, "创建时间", None, "2025-05-22T14:00:00Z"),
#                              "roles": ("list[str]", False, "角色列表", None, None),  # example置None，避免误判类型
#                          },
#             }
#         }
#
#     )