from django.db import transaction
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    HiddenField,
    ModelSerializer,
    SerializerMethodField,
)

from core.models import Compra, ItensCompra


class ItensCompraSerializer(ModelSerializer):

    total = SerializerMethodField()

    def get_total(self, instance):
        return instance.livro.preco * instance.quantidade

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'livro')
        depth = 1


class ItensCompraCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade')


class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(
        source='livro.titulo',
        read_only=True
    )

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'livro')
        depth = 1


class CompraCreateUpdateSerializer(ModelSerializer):
    usuario = HiddenField(default=CurrentUserDefault())

    itens = ItensCompraCreateUpdateSerializer(many=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens')

        compra = Compra.objects.create(**validated_data)

        for item in itens:
            ItensCompra.objects.create(
                compra=compra,
                **item
            )

        compra.save()

        return compra

    @transaction.atomic
    def update(self, compra, validated_data):
        itens = validated_data.pop('itens', None)

        if itens is not None:
            compra.itens.all().delete()

            for item in itens:
                ItensCompra.objects.create(
                    compra=compra,
                    **item
                )

        return super().update(compra, validated_data)


class CompraListSerializer(ModelSerializer):
    usuario = CharField(
        source='usuario.email',
        read_only=True
    )

    itens = ItensCompraListSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')


class CompraSerializer(ModelSerializer):
    usuario = CharField(
        source='usuario.email',
        read_only=True
    )

    status = CharField(
        source='get_status_display',
        read_only=True
    )

    itens = ItensCompraSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'itens')
