from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'tipo_pagamento', 'usuario__email']

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

    @extend_schema(
        request=None,
        responses={200: None},
        description='Gera um relatório de vendas do mês atual.',
        summary='Relatório de vendas do mês',
    )
    @action(detail=False, methods=['get'])
    def relatorio_vendas_mes(self, request):
        agora = timezone.now()

        inicio_mes = agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        compras = Compra.objects.filter(
            status=Compra.StatusCompra.FINALIZADO,
            data__gte=inicio_mes,
        )

        total_vendas = sum(
            compra.total for compra in compras
        )

        quantidade_vendas = compras.count()

        return Response(
            {
                'status': 'Relatório de vendas deste mês',
                'total_vendas': total_vendas,
                'quantidade_vendas': quantidade_vendas,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={200: None, 400: None},
        description=(
            'Finaliza a compra, verificando o estoque '
            'e atualizando a quantidade dos livros.'
        ),
        summary='Finalizar compra',
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        compra = self.get_object()

        # Verifica se a compra já foi finalizada.
        if compra.status == Compra.StatusCompra.FINALIZADO:
            return Response(
                {'status': 'Compra já finalizada'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        itens = list(compra.itens.select_related('livro').all())

        # Soma as quantidades caso o mesmo livro apareça
        # mais de uma vez na compra.
        quantidades_por_livro = {}

        for item in itens:
            livro_id = item.livro_id

            if livro_id not in quantidades_por_livro:
                quantidades_por_livro[livro_id] = {
                    'livro': item.livro,
                    'quantidade': 0,
                }

            quantidades_por_livro[livro_id]['quantidade'] += (
                item.quantidade
            )

        # Confere todo o estoque antes de alterar qualquer livro.
        for dados in quantidades_por_livro.values():
            livro = dados['livro']
            quantidade = dados['quantidade']

            if quantidade > livro.quantidade:
                return Response(
                    {
                        'status': 'Quantidade insuficiente',
                        'livro': livro.titulo,
                        'quantidade_disponivel': livro.quantidade,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Como todo o estoque já foi validado, atualiza os livros.
        for dados in quantidades_por_livro.values():
            livro = dados['livro']
            livro.quantidade -= dados['quantidade']
            livro.save()

        # Atualiza o status da compra.
        compra.status = Compra.StatusCompra.FINALIZADO
        compra.save()

        return Response(
            {'status': 'Compra finalizada'},
            status=status.HTTP_200_OK,
        )
