from rest_framework import mixins, viewsets

from .permissions import IsAuthorOrAdminOrReadOnly


class ListViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
