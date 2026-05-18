"""
Admin configuration para a app Picking.
Registra modelos no admin do Django.
"""

from django.contrib import admin
from .models import (
    Produto, Localizacao, ProdutoLocalizacao,
    Pedido, ItemPedido, Picking, Erro, TentativaValidacao
)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nome', 'cor', 'tamanho', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('sku', 'nome')
    readonly_fields = ('data_criacao', 'data_atualizacao')


@admin.register(Localizacao)
class LocalizacaoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'corredor', 'secao', 'nivel', 'ativo')
    list_filter = ('corredor', 'ativo')
    search_fields = ('corredor', 'secao', 'nivel')


@admin.register(ProdutoLocalizacao)
class ProdutoLocalizacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'localizacao', 'quantidade', 'quantidade_reservada')
    search_fields = ('produto__sku', 'localizacao__corredor')
    readonly_fields = ('data_atualizacao',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'status', 'data_criacao', 'data_conclusao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('numero_pedido',)
    readonly_fields = ('data_criacao',)


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'quantidade_coletada', 'status')
    list_filter = ('status', 'data_criacao')
    search_fields = ('pedido__numero_pedido', 'produto__sku')
    readonly_fields = ('data_criacao',)


@admin.register(Picking)
class PickingAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pedido', 'status', 'inicio', 'fim')
    list_filter = ('status', 'inicio')
    search_fields = ('usuario__username', 'pedido__numero_pedido')
    readonly_fields = ('inicio',)


@admin.register(Erro)
class ErroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'data_hora', 'resolvido', 'pedido')
    list_filter = ('tipo', 'resolvido', 'data_hora')
    search_fields = ('usuario__username', 'pedido__numero_pedido')
    readonly_fields = ('data_hora',)


@admin.register(TentativaValidacao)
class TentativaValidacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'sku_informado', 'resultado', 'data_hora')
    list_filter = ('resultado', 'data_hora')
    search_fields = ('usuario__username', 'sku_informado')
    readonly_fields = ('data_hora',)
