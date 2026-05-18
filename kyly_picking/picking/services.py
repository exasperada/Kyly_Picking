"""
Services do sistema Kyly Picking.
Centraliza regras de negocio, validacoes e metricas.
"""

from django.contrib.auth.models import User
from django.db.models import Count, Sum

from .models import Erro, Pedido, Picking, Produto, ProdutoLocalizacao, TentativaValidacao


class PickingService:
    """
    Regras de negocio ligadas ao fluxo de picking.
    """

    @staticmethod
    def validar_sku(usuario, item_pedido, sku_informado):
        resultado = {
            "sucesso": False,
            "mensagem": "",
            "tipo_resultado": "",
            "item_pedido": None,
        }

        sku_informado = (sku_informado or "").strip().upper()
        produto_lido = Produto.objects.filter(sku__iexact=sku_informado).first()

        if produto_lido is None:
            resultado["tipo_resultado"] = "sku_invalida"
            resultado["mensagem"] = "SKU invalida"
            PickingService._registrar_tentativa(
                usuario, item_pedido, sku_informado, "sku_invalida", resultado["mensagem"]
            )
            return resultado

        if produto_lido.id != item_pedido.produto_id:
            resultado["tipo_resultado"] = "item_nao_pertence"
            resultado["mensagem"] = "Item nao pertence ao pedido"
            PickingService._registrar_tentativa(
                usuario, item_pedido, sku_informado, "outro", resultado["mensagem"]
            )
            return resultado

        if item_pedido.quantidade_coletada >= item_pedido.quantidade:
            resultado["tipo_resultado"] = "quantidade_atingida"
            resultado["mensagem"] = "Quantidade ja atingida"
            PickingService._registrar_tentativa(
                usuario, item_pedido, sku_informado, "quantidade_atingida", resultado["mensagem"]
            )
            return resultado

        resultado["sucesso"] = True
        resultado["tipo_resultado"] = "sucesso"
        resultado["mensagem"] = "Produto confirmado"
        resultado["item_pedido"] = item_pedido

        PickingService._registrar_tentativa(
            usuario, item_pedido, sku_informado, "sucesso", resultado["mensagem"]
        )
        return resultado

    @staticmethod
    def _registrar_tentativa(usuario, item_pedido, sku_informado, resultado, mensagem):
        TentativaValidacao.objects.create(
            usuario=usuario,
            item_pedido=item_pedido,
            sku_informado=sku_informado,
            resultado=resultado,
            mensagem=mensagem,
        )

    @staticmethod
    def confirmar_coleta(usuario, item_pedido, quantidade=1):
        quantidade_anterior = item_pedido.quantidade_coletada
        item_pedido.quantidade_coletada = min(
            item_pedido.quantidade, item_pedido.quantidade_coletada + quantidade
        )
        item_pedido.status = (
            "confirmado"
            if item_pedido.quantidade_coletada >= item_pedido.quantidade
            else "em_picking"
        )
        item_pedido.save(update_fields=["quantidade_coletada", "status"])

        estoque = ProdutoLocalizacao.objects.filter(
            produto=item_pedido.produto,
            localizacao=item_pedido.localizacao,
        ).first()
        if estoque:
            estoque.quantidade = max(0, estoque.quantidade - quantidade)
            estoque.save(update_fields=["quantidade"])

        return {
            "sucesso": True,
            "quantidade_anterior": quantidade_anterior,
            "quantidade_nova": item_pedido.quantidade_coletada,
            "item_completo": item_pedido.quantidade_coletada >= item_pedido.quantidade,
            "mensagem": "Coleta confirmada com sucesso!",
        }

    @staticmethod
    def registrar_erro(usuario, pedido, produto, tipo_erro, descricao):
        return Erro.objects.create(
            usuario=usuario,
            pedido=pedido,
            produto=produto,
            tipo=tipo_erro,
            descricao=descricao,
        )

    @staticmethod
    def marcar_item_em_falta(usuario, item_pedido, descricao=""):
        mensagem_padrao = (
            descricao
            or f"Produto indisponivel na localizacao atual {item_pedido.localizacao}"
        )
        Erro.objects.create(
            usuario=usuario,
            pedido=item_pedido.pedido,
            produto=item_pedido.produto,
            tipo="item_falta",
            descricao=mensagem_padrao,
        )

        localizacao_alternativa = PickingService.sugerir_localizacao_alternativa(
            item_pedido.produto, item_pedido.localizacao_id
        )

        item_pedido.status = "falta"
        if localizacao_alternativa:
            item_pedido.localizacao = localizacao_alternativa
            item_pedido.status = "pendente"
        item_pedido.save(update_fields=["status", "localizacao"])

        return {
            "sucesso": True,
            "item_pendente": True,
            "mensagem": "Item marcado como em falta",
            "localizacao_alternativa": localizacao_alternativa,
        }

    @staticmethod
    def sugerir_localizacao_alternativa(produto, localizacao_atual_id=None):
        """
        Ponto de extensao futuro para algoritmos de grafos, IA ou ML.
        A implementacao atual usa ordenacao basica por corredor, secao e nivel.
        """

        localizacoes = (
            ProdutoLocalizacao.objects.filter(produto=produto, quantidade__gt=0)
            .exclude(localizacao_id=localizacao_atual_id)
            .select_related("localizacao")
            .order_by(
                "localizacao__corredor",
                "localizacao__secao",
                "localizacao__nivel",
            )
        )
        if localizacoes.exists():
            return localizacoes.first().localizacao
        return None


class RotaService:
    """
    Organizacao inicial de rotas.

    Futuramente pode evoluir para:
    - grafos com menor caminho;
    - heuristicas tipo TSP;
    - IA/ML com base em historico e congestionamento de corredores.
    """

    @staticmethod
    def otimizar_rota(itens_pedido):
        return list(
            itens_pedido.order_by(
                "localizacao__corredor",
                "localizacao__secao",
                "localizacao__nivel",
                "produto__sku",
            )
        )

    @staticmethod
    def calcular_distancia_estimada(itens_ordenados):
        distancia = 0
        localizacao_anterior = None

        for item in itens_ordenados:
            if localizacao_anterior and item.localizacao:
                distancia += (
                    abs(ord(item.localizacao.corredor[0]) - ord(localizacao_anterior.corredor[0]))
                    * 10
                )
                try:
                    distancia += abs(int(item.localizacao.secao) - int(localizacao_anterior.secao)) * 5
                except ValueError:
                    distancia += 5
            localizacao_anterior = item.localizacao

        return distancia


class DashboardService:
    @staticmethod
    def obter_estatisticas_gerais():
        return {
            "total_pedidos": Pedido.objects.count(),
            "pedidos_pendentes": Pedido.objects.filter(status="pendente").count(),
            "pedidos_em_picking": Pedido.objects.filter(status="em_picking").count(),
            "pedidos_concluidos": Pedido.objects.filter(status="concluido").count(),
            "total_erros": Erro.objects.count(),
            "erros_nao_resolvidos": Erro.objects.filter(resolvido=False).count(),
            "total_operadores": User.objects.filter(groups__name="Operador").count(),
            "total_coletas": Picking.objects.filter(status="concluido").count(),
        }

    @staticmethod
    def obter_produtividade_operadores():
        operadores = []
        usuarios = User.objects.filter(groups__name="Operador")

        for usuario in usuarios:
            pickings = Picking.objects.filter(usuario=usuario)
            total_picking = pickings.count()
            total_conclusoes = pickings.filter(status="concluido").count()
            tempo_total = pickings.aggregate(tempo=Sum("duracao_segundos"))["tempo"] or 0

            operadores.append(
                {
                    "usuario": usuario.get_full_name() or usuario.username,
                    "total_picking": total_picking,
                    "total_conclusoes": total_conclusoes,
                    "tempo_total_horas": tempo_total / 3600,
                    "taxa_conclusao": (total_conclusoes / total_picking * 100) if total_picking else 0,
                }
            )

        return operadores

    @staticmethod
    def obter_erros_por_tipo():
        return list(Erro.objects.values("tipo").annotate(count=Count("id")).order_by("-count"))

    @staticmethod
    def obter_erros_por_operador():
        return list(
            Erro.objects.values("usuario__username").annotate(count=Count("id")).order_by("-count")
        )

    @staticmethod
    def obter_tempo_medio_picking():
        pickings = Picking.objects.filter(status="concluido")
        if not pickings.exists():
            return 0
        tempo_total = pickings.aggregate(tempo=Sum("duracao_segundos"))["tempo"] or 0
        return tempo_total / pickings.count()

    @staticmethod
    def obter_taxa_erro():
        total_pickings = Picking.objects.count()
        if total_pickings == 0:
            return 0
        return (Erro.objects.count() / total_pickings) * 100
