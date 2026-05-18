"""
Carga de dados de demonstracao para o Kyly Picking.
"""

import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.utils import timezone

from picking.models import Erro, ItemPedido, Localizacao, Pedido, Picking, Produto, ProdutoLocalizacao


def criar_grupos():
    Group.objects.get_or_create(name="Operador")
    Group.objects.get_or_create(name="Gestor")
    print("Grupos criados.")


def criar_usuarios():
    if not User.objects.filter(username="operator").exists():
        operator = User.objects.create_user(
            username="operator",
            email="operator@kyly.com",
            password="123456",
            first_name="Joao",
            last_name="Silva",
        )
        operator.groups.add(Group.objects.get(name="Operador"))
        print("Usuario operator criado.")

    if not User.objects.filter(username="manager").exists():
        manager = User.objects.create_user(
            username="manager",
            email="manager@kyly.com",
            password="123456",
            first_name="Maria",
            last_name="Santos",
        )
        manager.groups.add(Group.objects.get(name="Gestor"))
        print("Usuario manager criado.")

    for index in range(2, 5):
        username = f"operator{index}"
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password="123456",
                first_name=f"Operador {index}",
                last_name="Demo",
            )
            user.groups.add(Group.objects.get(name="Operador"))
            print(f"Usuario {username} criado.")


def criar_localizacoes():
    corredores = ["A", "B", "C", "D", "E"]
    secoes = ["01", "02", "03", "04", "05"]
    niveis = ["1A", "1B", "2A"]

    count = 0
    for corredor in corredores:
        for secao in secoes:
            for nivel in niveis:
                _, created = Localizacao.objects.get_or_create(
                    corredor=corredor,
                    secao=secao,
                    nivel=nivel,
                    defaults={"descricao": f"Endereco {corredor}-{secao}-{nivel}"},
                )
                if created:
                    count += 1
    print(f"{count} localizacoes criadas.")


def criar_produtos():
    produtos_dados = [
        ("SKU001", "Camiseta Basica", "Branco"),
        ("SKU002", "Camiseta Basica", "Preto"),
        ("SKU003", "Calca Jeans", "Azul"),
        ("SKU004", "Jaqueta Inverno", "Preto"),
        ("SKU005", "Sapato Casual", "Marrom"),
        ("SKU006", "Bolsa de Couro", "Preto"),
        ("SKU007", "Cinto Casual", "Marrom"),
        ("SKU008", "Meias Algodao", "Branco"),
        ("SKU009", "Lenco Seda", "Vermelho"),
        ("SKU010", "Gravata Formal", "Azul"),
    ]

    localizacoes = list(Localizacao.objects.all())
    count = 0
    for sku, nome, cor in produtos_dados:
        produto, created = Produto.objects.get_or_create(
            sku=sku,
            defaults={
                "nome": nome,
                "cor": cor,
                "tamanho": "M",
                "descricao": f"{nome} - cor {cor}",
                "ativo": True,
            },
        )
        if created:
            count += 1

        for localizacao in random.sample(localizacoes, k=min(3, len(localizacoes))):
            ProdutoLocalizacao.objects.get_or_create(
                produto=produto,
                localizacao=localizacao,
                defaults={"quantidade": random.randint(10, 100)},
            )

    print(f"{count} produtos criados.")


def criar_pedidos():
    produtos = list(Produto.objects.all())
    count = 0

    for index in range(1, 6):
        numero_pedido = f"PED{index:05d}"
        if Pedido.objects.filter(numero_pedido=numero_pedido).exists():
            continue

        pedido = Pedido.objects.create(numero_pedido=numero_pedido, status="pendente")
        for produto in random.sample(produtos, k=min(random.randint(3, 5), len(produtos))):
            estoque = ProdutoLocalizacao.objects.filter(produto=produto).select_related("localizacao").first()
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                localizacao=estoque.localizacao if estoque else None,
                quantidade=random.randint(1, 5),
                status="pendente",
            )
        count += 1

    print(f"{count} pedidos criados.")


def criar_pickings():
    operadores = list(User.objects.filter(groups__name="Operador"))
    pedidos = list(Pedido.objects.all()[:3])
    count = 0

    for pedido in pedidos:
        if Picking.objects.filter(pedido=pedido).exists():
            continue
        operador = random.choice(operadores)
        inicio = timezone.now() - timedelta(days=random.randint(0, 3))
        fim = inicio + timedelta(minutes=random.randint(10, 40))

        Picking.objects.create(
            usuario=operador,
            pedido=pedido,
            status="concluido",
            inicio=inicio,
            fim=fim,
            duracao_segundos=int((fim - inicio).total_seconds()),
        )

        for item in pedido.itens.all():
            item.status = "confirmado"
            item.quantidade_coletada = item.quantidade
            item.save(update_fields=["status", "quantidade_coletada"])

        pedido.status = "concluido"
        pedido.data_conclusao = fim
        pedido.save(update_fields=["status", "data_conclusao"])
        count += 1

    print(f"{count} pickings de demonstracao criados.")


def criar_erros():
    operadores = list(User.objects.filter(groups__name="Operador"))
    pedidos = list(Pedido.objects.all())
    produtos = list(Produto.objects.all())
    tipos_erro = [
        "sku_invalida",
        "quantidade_excessiva",
        "produto_nao_encontrado",
        "localizacao_errada",
        "item_falta",
    ]

    count = 0
    for _ in range(10):
        Erro.objects.create(
            usuario=random.choice(operadores),
            pedido=random.choice(pedidos),
            produto=random.choice(produtos),
            tipo=random.choice(tipos_erro),
            descricao="Erro de demonstracao para analise do dashboard.",
            resolvido=random.choice([True, False]),
        )
        count += 1
    print(f"{count} erros criados.")


def limpar_dados():
    print("Limpando dados anteriores...")
    ItemPedido.objects.all().delete()
    Picking.objects.all().delete()
    Erro.objects.all().delete()
    ProdutoLocalizacao.objects.all().delete()
    Pedido.objects.all().delete()
    Produto.objects.all().delete()
    Localizacao.objects.all().delete()
    User.objects.filter(username__startswith="operator").delete()
    User.objects.filter(username__startswith="manager").delete()
    print("Dados removidos.")


def popular_banco_dados(limpar=False):
    print("=" * 60)
    print("KYLY PICKING - CARGA DE DADOS")
    print("=" * 60)

    if limpar:
        limpar_dados()

    criar_grupos()
    criar_usuarios()
    criar_localizacoes()
    criar_produtos()
    criar_pedidos()
    criar_pickings()
    criar_erros()

    print("=" * 60)
    print("Carga concluida com sucesso.")
    print("Operador: operator / 123456")
    print("Gestor: manager / 123456")
    print("URL: http://localhost:8000/login/")
    print("=" * 60)
