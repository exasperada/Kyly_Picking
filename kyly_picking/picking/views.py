"""
Views do sistema Kyly Picking.
"""

import base64
import io
import json
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from PIL import Image, ImageEnhance, ImageOps
import zxingcpp

from .models import Erro, ItemPedido, Pedido, Picking
from .services import DashboardService, PickingService, RotaService


def _eh_gestor(user):
    return user.groups.filter(name="Gestor").exists()


def _eh_operador(user):
    return user.groups.filter(name="Operador").exists()


def _pagina_contexto(total_itens, pagina, por_pagina=20):
    total_paginas = max(1, (total_itens + por_pagina - 1) // por_pagina)
    pagina = max(1, min(pagina, total_paginas))
    return {
        "pagina_atual": pagina,
        "total_paginas": total_paginas,
        "page_numbers": list(range(1, total_paginas + 1)),
        "slice_start": (pagina - 1) * por_pagina,
        "slice_end": pagina * por_pagina,
    }


def _decode_image_from_payload(image_data):
    if not image_data or "," not in image_data:
        return None

    _, encoded = image_data.split(",", 1)
    binary = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(binary))
    image.load()
    return image


def _decode_barcode_text(image_data):
    image = _decode_image_from_payload(image_data)
    if image is None:
        return None

    variants = [
        image.convert("RGB"),
        ImageOps.autocontrast(image.convert("L")),
    ]

    grayscale = ImageOps.autocontrast(image.convert("L"))
    variants.append(ImageEnhance.Contrast(grayscale).enhance(2.2))
    variants.append(grayscale.resize((grayscale.width * 2, grayscale.height * 2)))
    variants.append(
        ImageOps.autocontrast(image.convert("RGB")).resize((image.width * 2, image.height * 2))
    )

    threshold = grayscale.point(lambda p: 255 if p > 150 else 0)
    variants.append(threshold)

    for variant in variants:
        result = zxingcpp.read_barcode(variant)
        if result and result.text:
            return result.text.strip().upper()

    return None


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect("dashboard")

        response = render(request, "login.html", {"erro": "Usuario ou senha incorretos"})
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    response = render(request, "login.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@csrf_exempt
@require_http_methods(["POST"])
def api_scan_login_code(request):
    try:
        data = json.loads(request.body)
        code_text = _decode_barcode_text(data.get("image"))
        return JsonResponse({"sucesso": True, "codigo": code_text or ""})
    except (json.JSONDecodeError, ValueError, OSError):
        return JsonResponse({"sucesso": False, "mensagem": "Imagem invalida para leitura."}, status=400)


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def dashboard_view(request):
    return dashboard_gestor(request) if _eh_gestor(request.user) else tela_picking(request)


@login_required(login_url="login")
def dashboard_gestor(request):
    if not _eh_gestor(request.user):
        return HttpResponseForbidden("Acesso restrito ao gestor.")

    stats = DashboardService.obter_estatisticas_gerais()
    produtividade = DashboardService.obter_produtividade_operadores()
    erros_tipo = DashboardService.obter_erros_por_tipo()
    erros_operador = DashboardService.obter_erros_por_operador()
    tempo_medio = DashboardService.obter_tempo_medio_picking()
    taxa_erro = DashboardService.obter_taxa_erro()

    data_limite = timezone.now() - timedelta(days=7)
    erros_recentes = (
        Erro.objects.filter(data_hora__gte=data_limite)
        .select_related("usuario", "pedido", "produto")[:10]
    )

    taxa_conclusao_geral = (
        (stats["pedidos_concluidos"] / stats["total_pedidos"]) * 100 if stats["total_pedidos"] else 0
    )

    context = {
        "stats": stats,
        "produtividade": produtividade,
        "erros_tipo": erros_tipo,
        "erros_operador": erros_operador,
        "tempo_medio": tempo_medio,
        "taxa_erro": taxa_erro,
        "taxa_conclusao_geral": taxa_conclusao_geral,
        "erros_recentes": erros_recentes,
    }
    return render(request, "dashboard_gestor.html", context)


@login_required(login_url="login")
def tela_picking(request):
    if _eh_gestor(request.user):
        return redirect("dashboard")

    picking_ativo = (
        Picking.objects.filter(usuario=request.user, status__in=["iniciado", "em_progresso"])
        .select_related("pedido")
        .first()
    )

    pedido = None
    item_atual = None
    proximos_itens = []
    progresso = 0
    distancia_estimada = 0

    if picking_ativo:
        pedido = picking_ativo.pedido
        itens_pendentes = (
            pedido.itens.filter(status__in=["pendente", "em_picking", "falta"])
            .select_related("produto", "localizacao")
        )

        if itens_pendentes.exists():
            itens_otimizados = RotaService.otimizar_rota(itens_pendentes)
            item_atual = itens_otimizados[0]
            proximos_itens = itens_otimizados[1:6]
            distancia_estimada = RotaService.calcular_distancia_estimada(itens_otimizados)

        progresso = pedido.percentual_progresso()

    pedidos_disponiveis = (
        Pedido.objects.filter(status__in=["pendente", "em_picking"])
        .exclude(pickings__status__in=["iniciado", "em_progresso"])
        .prefetch_related("itens")[:8]
    )

    context = {
        "picking_ativo": picking_ativo,
        "pedido": pedido,
        "item_atual": item_atual,
        "proximos_itens": proximos_itens,
        "progresso": progresso,
        "pedidos_disponiveis": pedidos_disponiveis,
        "distancia_estimada": distancia_estimada,
    }
    return render(request, "picking.html", context)


@login_required(login_url="login")
@require_http_methods(["POST"])
def iniciar_picking(request):
    if not _eh_operador(request.user):
        return JsonResponse({"sucesso": False, "mensagem": "Apenas operadores podem iniciar picking."}, status=403)

    try:
        data = json.loads(request.body)
        numero_pedido = data.get("numero_pedido")
        if not numero_pedido:
            return JsonResponse({"sucesso": False, "mensagem": "Numero do pedido e obrigatorio."}, status=400)

        pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
        if pedido.status in ["concluido", "cancelado"]:
            return JsonResponse({"sucesso": False, "mensagem": "Pedido nao pode mais ser iniciado."}, status=400)

        if Picking.objects.filter(usuario=request.user, status__in=["iniciado", "em_progresso"]).exists():
            return JsonResponse({"sucesso": False, "mensagem": "Finalize o picking atual antes de iniciar outro."}, status=400)

        if Picking.objects.filter(pedido=pedido, status__in=["iniciado", "em_progresso"]).exists():
            return JsonResponse({"sucesso": False, "mensagem": "Este pedido ja esta em picking por outro operador."}, status=400)

        picking = Picking.objects.create(usuario=request.user, pedido=pedido, status="em_progresso")
        pedido.status = "em_picking"
        pedido.save(update_fields=["status"])

        return JsonResponse(
            {
                "sucesso": True,
                "mensagem": "Picking iniciado com sucesso.",
                "picking_id": picking.id,
                "pedido_id": pedido.id,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def validar_sku(request):
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        sku_informado = data.get("sku_informado", "")
        quantidade = int(data.get("quantidade", 1))

        item_pedido = get_object_or_404(
            ItemPedido.objects.select_related("pedido", "produto", "localizacao"),
            id=item_id,
        )

        picking_ativo = Picking.objects.filter(
            usuario=request.user,
            pedido=item_pedido.pedido,
            status__in=["iniciado", "em_progresso"],
        ).exists()
        if not picking_ativo:
            return JsonResponse({"sucesso": False, "mensagem": "Pedido nao esta ativo para este operador."}, status=403)

        resultado_validacao = PickingService.validar_sku(request.user, item_pedido, sku_informado)
        if not resultado_validacao["sucesso"]:
            return JsonResponse(
                {
                    "sucesso": False,
                    "mensagem": resultado_validacao["mensagem"],
                    "tipo": resultado_validacao["tipo_resultado"],
                },
                status=400,
            )

        resultado_coleta = PickingService.confirmar_coleta(request.user, item_pedido, quantidade)

        pedido = item_pedido.pedido
        itens_abertos = pedido.itens.exclude(status="confirmado").count()
        pedido_completo = itens_abertos == 0

        if pedido_completo:
            pedido.status = "concluido"
            pedido.data_conclusao = timezone.now()
            pedido.save(update_fields=["status", "data_conclusao"])

            picking = Picking.objects.filter(usuario=request.user, pedido=pedido).last()
            if picking:
                picking.status = "concluido"
                picking.fim = timezone.now()
                picking.duracao_segundos = picking.calcular_duracao()
                picking.save(update_fields=["status", "fim", "duracao_segundos"])

        return JsonResponse(
            {
                "sucesso": True,
                "mensagem": resultado_validacao["mensagem"],
                "item_completo": resultado_coleta["item_completo"],
                "quantidade_nova": resultado_coleta["quantidade_nova"],
                "pedido_completo": pedido_completo,
                "progresso": pedido.percentual_progresso(),
            }
        )
    except (TypeError, ValueError):
        return JsonResponse({"sucesso": False, "mensagem": "Quantidade invalida."}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def reportar_erro(request):
    try:
        data = json.loads(request.body)
        item_pedido = get_object_or_404(ItemPedido.objects.select_related("pedido", "produto"), id=data.get("item_id"))
        tipo_erro = data.get("tipo_erro", "outro")
        descricao = data.get("descricao", "").strip() or "Ocorrencia informada pelo operador."

        PickingService.registrar_erro(
            request.user,
            item_pedido.pedido,
            item_pedido.produto,
            tipo_erro,
            descricao,
        )
        return JsonResponse({"sucesso": True, "mensagem": "Erro reportado com sucesso."})
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def item_em_falta(request):
    try:
        data = json.loads(request.body)
        item_pedido = get_object_or_404(
            ItemPedido.objects.select_related("pedido", "produto", "localizacao"),
            id=data.get("item_id"),
        )
        resultado = PickingService.marcar_item_em_falta(request.user, item_pedido, data.get("descricao", ""))

        mensagem = resultado["mensagem"]
        localizacao_alternativa = None
        if resultado["localizacao_alternativa"]:
            loc = resultado["localizacao_alternativa"]
            localizacao_alternativa = loc.endereco_completo()
            mensagem = f"{mensagem}. Nova sugestao: {localizacao_alternativa}."

        return JsonResponse(
            {
                "sucesso": True,
                "mensagem": mensagem,
                "localizacao_alternativa": localizacao_alternativa,
                "item_pendente": True,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def proxima_coleta(request):
    try:
        data = json.loads(request.body)
        pedido = get_object_or_404(Pedido, id=data.get("pedido_id"))
        itens_pendentes = pedido.itens.filter(status__in=["pendente", "em_picking"]).select_related("produto", "localizacao")

        if not itens_pendentes.exists():
            return JsonResponse(
                {
                    "sucesso": True,
                    "mensagem": "Todos os itens foram coletados.",
                    "proxima_coleta": None,
                    "pedido_completo": True,
                }
            )

        item = RotaService.otimizar_rota(itens_pendentes)[0]
        item.status = "em_picking"
        item.save(update_fields=["status"])

        return JsonResponse(
            {
                "sucesso": True,
                "proxima_coleta": {
                    "id": item.id,
                    "produto": {
                        "nome": item.produto.nome,
                        "sku": item.produto.sku,
                        "cor": item.produto.cor,
                        "tamanho": item.produto.tamanho,
                    },
                    "quantidade": item.quantidade,
                    "quantidade_coletada": item.quantidade_coletada,
                    "localizacao": {
                        "corredor": item.localizacao.corredor if item.localizacao else "-",
                        "secao": item.localizacao.secao if item.localizacao else "-",
                        "nivel": item.localizacao.nivel if item.localizacao else "-",
                        "endereco_completo": item.localizacao.endereco_completo() if item.localizacao else "Sem localizacao",
                    },
                    "faltando_coletar": item.faltando_coletar(),
                },
                "progresso": pedido.percentual_progresso(),
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def pular_item(request):
    try:
        data = json.loads(request.body)
        item_pedido = get_object_or_404(
            ItemPedido.objects.select_related("pedido", "produto", "localizacao"),
            id=data.get("item_id"),
        )
        item_pedido.status = "pendente"
        item_pedido.save(update_fields=["status"])

        return JsonResponse(
            {
                "sucesso": True,
                "mensagem": "Item pulado e recolocado na fila.",
                "pedido_id": item_pedido.pedido_id,
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"sucesso": False, "mensagem": "Payload invalido."}, status=400)


@login_required(login_url="login")
@require_http_methods(["POST"])
def api_scan_item_code(request):
    try:
        data = json.loads(request.body)
        code_text = _decode_barcode_text(data.get("image"))
        return JsonResponse({"sucesso": True, "codigo": code_text or ""})
    except (json.JSONDecodeError, ValueError, OSError):
        return JsonResponse({"sucesso": False, "mensagem": "Imagem invalida para leitura."}, status=400)


@login_required(login_url="login")
def historico_erros(request):
    erros = Erro.objects.select_related("usuario", "pedido", "produto")
    if not _eh_gestor(request.user):
        erros = erros.filter(usuario=request.user)

    tipo = request.GET.get("tipo")
    if tipo:
        erros = erros.filter(tipo=tipo)

    try:
        pagina = int(request.GET.get("pagina", 1))
    except ValueError:
        pagina = 1

    total_erros = erros.count()
    paginacao = _pagina_contexto(total_erros, pagina)
    context = {
        "erros": erros.order_by("-data_hora")[paginacao["slice_start"]:paginacao["slice_end"]],
        "total_erros": total_erros,
        "filtro_tipo": tipo or "",
        **{k: v for k, v in paginacao.items() if not k.startswith("slice_")},
    }
    return render(request, "historico_erros.html", context)


@login_required(login_url="login")
def historico_pedidos(request):
    pedidos = Pedido.objects.prefetch_related("itens__produto")
    if not _eh_gestor(request.user):
        pedidos = pedidos.filter(pickings__usuario=request.user).distinct()

    status = request.GET.get("status")
    if status:
        pedidos = pedidos.filter(status=status)

    try:
        pagina = int(request.GET.get("pagina", 1))
    except ValueError:
        pagina = 1

    total_pedidos = pedidos.count()
    paginacao = _pagina_contexto(total_pedidos, pagina)
    context = {
        "pedidos": pedidos.order_by("-data_criacao")[paginacao["slice_start"]:paginacao["slice_end"]],
        "total_pedidos": total_pedidos,
        "filtro_status": status or "",
        **{k: v for k, v in paginacao.items() if not k.startswith("slice_")},
    }
    return render(request, "historico_pedidos.html", context)


@login_required(login_url="login")
@require_http_methods(["GET"])
def api_dados_dashboard(request):
    if not _eh_gestor(request.user):
        return JsonResponse({"mensagem": "Acesso restrito ao gestor."}, status=403)

    stats = DashboardService.obter_estatisticas_gerais()
    produtividade = DashboardService.obter_produtividade_operadores()
    erros_tipo = DashboardService.obter_erros_por_tipo()
    taxa_erro = DashboardService.obter_taxa_erro()
    tempo_medio = DashboardService.obter_tempo_medio_picking()

    return JsonResponse(
        {
            "stats": stats,
            "produtividade": produtividade,
            "erros_tipo": erros_tipo,
            "taxa_erro": round(taxa_erro, 2),
            "tempo_medio_segundos": round(tempo_medio, 2),
        }
    )


@login_required(login_url="login")
@require_http_methods(["GET"])
def api_proxima_coleta(request):
    pedido = get_object_or_404(Pedido, id=request.GET.get("pedido_id"))
    itens_pendentes = pedido.itens.filter(status__in=["pendente", "em_picking"]).select_related("produto", "localizacao")

    if not itens_pendentes.exists():
        return JsonResponse({"sucesso": True, "proxima_coleta": None, "mensagem": "Pedido concluido"})

    item = RotaService.otimizar_rota(itens_pendentes)[0]
    return JsonResponse(
        {
            "sucesso": True,
            "proxima_coleta": {
                "id": item.id,
                "produto": {"nome": item.produto.nome, "sku": item.produto.sku},
                "quantidade": item.quantidade,
                "localizacao": item.localizacao.endereco_completo() if item.localizacao else "Sem localizacao",
            },
        }
    )
