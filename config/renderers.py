
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

#配置返回结构
RESPONSE_TEMPLATE_CONFIG = {
    "field_order": ["code", "msg", "data"], #配置顺序（code顺序不要变）
    "fields": {
        "code": {"type": "integer", "example": 200, "default": 200},
        "msg": {"type": "string", "example": "ok", "default": "ok"},
        "data": {"type": "any", "default": None}, #detault为None代表返回数据的schema结构
    }
}
def build_response(data=None, code=None, message=None, is_error=False):
    cfg = RESPONSE_TEMPLATE_CONFIG
    resp = {}
    for key in cfg["field_order"]:
        field = cfg["fields"][key]

        if key == cfg["field_order"][0]:  # 通常是 code 字段
            resp[key] = code if code is not None else field.get("default", 0)
        elif "msg" in key or "message" in key:
            resp[key] = message if message is not None else field.get("default", "success")
        elif field.get("default") is None:
            resp[key] = data  # data 占位字段 → 替换为实际数据
        else:
            resp[key] = field.get("default")

    return resp

#将django drf 返回的内容包装成模板
class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response", None)
        template_keys = set(RESPONSE_TEMPLATE_CONFIG["field_order"])
        """
        如果返回的数据是字典
        且已经包含了配置中要求的所有字段（如 code、message、data）
        就直接返回（说明已经是标准格式了，不需要重复包装）
        """
        if isinstance(data, dict) and template_keys <= set(data.keys()):
            return super().render(data, accepted_media_type, renderer_context)
        """
        处理错误响应
        """
        if response and not str(response.status_code).startswith("2"):
            code = response.status_code
            message = data.get("detail") if isinstance(data, dict) and 'detail' in data else data
            return super().render(build_response(code=code, message=message, is_error=True), accepted_media_type, renderer_context)
        """
        如果结构不对，那就把 data 包进响应模板中。
        """
        return super().render(build_response(data=data), accepted_media_type, renderer_context)

# 将django drf spectacular返回的schema格式封装成模板
def wrap_schema_with_three_stage(result, generator, request, public):
    if "components" not in result:
        return result

    cfg = RESPONSE_TEMPLATE_CONFIG
    field_order = cfg["field_order"]
    field_definitions = cfg["fields"]

    for path_item in result.get("paths", {}).values():
        for operation in path_item.values():
            responses = operation.get("responses", {})
            for response in responses.values():
                for content_schema in response.get("content", {}).values():
                    original_schema = content_schema.get("schema")
                    if original_schema:
                        properties = {}
                        required = []

                        for key in field_order:
                            field = field_definitions[key]
                            if field.get("default") is None:
                                # data 占位字段 → 使用原始 schema
                                properties[key] = original_schema
                            else:
                                properties[key] = {
                                    k: v for k, v in field.items() if k != "default"
                                }
                            required.append(key)

                        content_schema["schema"] = {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }

    return result

def custom_response(data=None, code=None, msg=None, status=None, **kwargs):
    """
    构建符合 RESPONSE_TEMPLATE_CONFIG 的响应结构
    - data: 主要数据
    - code: 状态码，可覆盖配置默认
    - msg: 提示信息，可覆盖配置默认
    - status: DRF 的 HTTP 状态码（默认自动判断）
    """
    cfg = RESPONSE_TEMPLATE_CONFIG
    field_order = cfg["field_order"]
    fields = cfg["fields"]

    result = {}
    for field in field_order:
        default = fields[field].get("default")

        # data 字段特殊处理：default=None 说明它占位实际响应体
        if default is None:
            result[field] = data
        else:
            result[field] = {
                "code": code,
                "msg": msg
            }.get(field, default)

    return Response(result, status=status, **kwargs)