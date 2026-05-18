from django.contrib.auth.models import Group, User
from django.test import TestCase

from picking.models import ItemPedido, Localizacao, Pedido, Produto, ProdutoLocalizacao
from picking.services import PickingService


class PickingServiceTests(TestCase):
    def setUp(self):
        self.operador_group = Group.objects.create(name="Operador")
        self.user = User.objects.create_user(username="operator", password="123456")
        self.user.groups.add(self.operador_group)

        self.produto = Produto.objects.create(nome="Produto A", sku="SKU-A", cor="Azul", tamanho="M")
        self.produto_alt = Produto.objects.create(nome="Produto B", sku="SKU-B", cor="Preto", tamanho="G")
        self.localizacao = Localizacao.objects.create(corredor="A", secao="01", nivel="1A")
        self.localizacao_alt = Localizacao.objects.create(corredor="B", secao="02", nivel="1B")
        ProdutoLocalizacao.objects.create(produto=self.produto, localizacao=self.localizacao, quantidade=10)
        ProdutoLocalizacao.objects.create(produto=self.produto, localizacao=self.localizacao_alt, quantidade=5)

        self.pedido = Pedido.objects.create(numero_pedido="PED00001")
        self.item = ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            localizacao=self.localizacao,
            quantidade=2,
        )

    def test_validar_sku_com_sucesso(self):
        resultado = PickingService.validar_sku(self.user, self.item, "SKU-A")
        self.assertTrue(resultado["sucesso"])
        self.assertEqual(resultado["mensagem"], "Produto confirmado")

    def test_validar_sku_de_outro_produto(self):
        resultado = PickingService.validar_sku(self.user, self.item, "SKU-B")
        self.assertFalse(resultado["sucesso"])
        self.assertEqual(resultado["tipo_resultado"], "item_nao_pertence")

    def test_validar_sku_com_quantidade_atingida(self):
        self.item.quantidade_coletada = 2
        self.item.save()

        resultado = PickingService.validar_sku(self.user, self.item, "SKU-A")
        self.assertFalse(resultado["sucesso"])
        self.assertEqual(resultado["tipo_resultado"], "quantidade_atingida")

    def test_marcar_item_em_falta_troca_localizacao_quando_ha_alternativa(self):
        resultado = PickingService.marcar_item_em_falta(self.user, self.item)
        self.item.refresh_from_db()

        self.assertTrue(resultado["sucesso"])
        self.assertEqual(self.item.localizacao, self.localizacao_alt)
        self.assertEqual(self.item.status, "pendente")

