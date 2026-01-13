from rest_framework import routers
from .api_views import ActivityEntryViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'entries', ActivityEntryViewSet, basename='entries')

urlpatterns = [
    path('', include(router.urls)),
]
