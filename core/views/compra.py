
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Compra
from core.serializers.compra import (
    CompraCreateUpdateSerializer,
    CompraListSerializer,
    CompraSerializer,
)


class CompraViewSet(ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    http_method_names = ['get', 'post', 'put', 'delete']

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_fields = [
        'usuario__email',
        'status',
        'data',
    ]

    search_fields = ['usuario__email']

    ordering_fields = [
        'usuario__email',
        'status',
        'data',
    ]

    ordering = ['-data']

    def get_queryset(self):
        usuario = self.request.user

        if usuario.is_superuser:
            return Compra.objects.all()

        if usuario.groups.filter(name='administradores').exists():
            return Compra.objects.all()

        return Compra.objects.filter(usuario=usuario)

    def get_serializer_class(self):
        if self.action == 'list':
            return CompraListSerializer

        if self.action in {'create', 'update'}:
            return CompraCreateUpdateSerializer

        return CompraSerializer
