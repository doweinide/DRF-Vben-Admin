from rest_framework import serializers
from rest_framework.views import APIView
from config.renderers import custom_response

class HelloWorldDataSerializer(serializers.Serializer):
    id = serializers.CharField()

class HelloWorldView(APIView):
    # 序列化器声明data的schema
    serializer_class = HelloWorldDataSerializer
    def get(self, request):
        #返回数据要三段式符合要求
        return custom_response(data={"id":23},code=23)

