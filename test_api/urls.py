from django.urls import path
from .views import HelloWorldView

urlpatterns = [
    path("", HelloWorldView.as_view(), name="test-api"),  # 注意这里要加 .as_view()
]
