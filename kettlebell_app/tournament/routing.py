from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/amator-kobiety-do-65kg/$', consumers.ResultsConsumer.as_asgi()),
]