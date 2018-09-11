from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers
from .viewsets import LessonViewset
from .viewsets import ClassChannelViewset

router = routers.SimpleRouter()
router.register(r'lesson', LessonViewset, base_name='lesson')
router.register(r'classchannel', ClassChannelViewset, base_name='classchannel')

urlpatterns = [
    url(r'^', include(router.urls)),
]
