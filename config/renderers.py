
from rest_framework.renderers import JSONRenderer
#配置返回结构
RESPONSE_TEMPLATE_CONFIG = {
    "field_order": ["code", "msg", "data"], #配置顺序（不重要）
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

        if isinstance(data, dict) and template_keys <= set(data.keys()):
            return super().render(data, accepted_media_type, renderer_context)

        if response and not str(response.status_code).startswith("2"):
            code = response.status_code
            message = data.get("detail") if isinstance(data, dict) else "error"
            return super().render(build_response(code=code, message=message, is_error=True), accepted_media_type, renderer_context)

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
