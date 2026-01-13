from rest_framework import viewsets, permissions
from .models import ActivityEntry
from .serializers import ActivityEntrySerializer

class ActivityEntryViewSet(viewsets.ModelViewSet):
    queryset = ActivityEntry.objects.all().order_by('-start')
    serializer_class = ActivityEntrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
