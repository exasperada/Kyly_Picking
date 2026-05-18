import base64
import io

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image
import zxingcpp

from picking.models import ItemPedido, Localizacao, Pedido, Picking, Produto, ProdutoLocalizacao


class PickingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.operador_group = Group.objects.create(name="Operador")
        self.gestor_group = Group.objects.create(name="Gestor")

        self.operador = User.objects.create_user(username="operator", password="123456")
        self.operador.groups.add(self.operador_group)
        self.gestor = User.objects.create_user(username="manager", password="123456")
        self.gestor.groups.add(self.gestor_group)

        self.produto = Produto.objects.create(nome="Produto A", sku="SKU-A")
        self.localizacao = Localizacao.objects.create(corredor="A", secao="01", nivel="1A")
        ProdutoLocalizacao.objects.create(produto=self.produto, localizacao=self.localizacao, quantidade=20)
        self.pedido = Pedido.objects.create(numero_pedido="PED00001")
        self.item = ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            localizacao=self.localizacao,
            quantidade=1,
        )

    def _barcode_payload(self, text):
        barcode = zxingcpp.create_barcode(text, zxingcpp.BarcodeFormat.Code39)
        image = zxingcpp.write_barcode_to_image(barcode, 4)
        pil_image = Image.fromarray(image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def test_manager_access_dashboard_api(self):
        self.client.force_login(self.gestor)
        response = self.client.get(reverse("api_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_access_dashboard_api(self):
        self.client.force_login(self.operador)
        response = self.client.get(reverse("api_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_operator_can_start_picking(self):
        self.client.force_login(self.operador)
        response = self.client.post(
            reverse("iniciar_picking"),
            data='{"numero_pedido":"PED00001"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Picking.objects.filter(usuario=self.operador, pedido=self.pedido).exists())

    def test_operator_can_validate_and_finish_order(self):
        Picking.objects.create(usuario=self.operador, pedido=self.pedido, status="em_progresso")
        self.pedido.status = "em_picking"
        self.pedido.save()

        self.client.force_login(self.operador)
        response = self.client.post(
            reverse("validar_sku"),
            data='{"item_id": %s, "sku_informado":"SKU-A", "quantidade":1}' % self.item.id,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual(self.item.status, "confirmado")
        self.assertEqual(self.pedido.status, "concluido")

    def test_login_scan_api_decodes_badge(self):
        response = self.client.post(
            reverse("api_scan_login_code"),
            data=f'{{"image":"{self._barcode_payload("OPERATOR")}"}}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["codigo"], "OPERATOR")

    def test_item_scan_api_decodes_sku(self):
        self.client.force_login(self.operador)
        response = self.client.post(
            reverse("api_scan_item_code"),
            data=f'{{"image":"{self._barcode_payload("SKU-A")}"}}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["codigo"], "SKU-A")
