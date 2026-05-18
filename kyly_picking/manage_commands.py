"""
Comandos utilitarios para o ambiente local do Kyly Picking.
"""

import os
import sys

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kyly_picking.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core.management import call_command  # noqa: E402

from picking.fixtures import popular_banco_dados  # noqa: E402
from picking.models import Erro, ItemPedido, Pedido, Picking, Produto  # noqa: E402


def limpar_tudo():
    confirmacao = input("Digite SIM para limpar todo o banco: ").strip().upper()
    if confirmacao != "SIM":
        print("Operacao cancelada.")
        return

    call_command("flush", verbosity=0, interactive=False)
    call_command("migrate", verbosity=0)
    popular_banco_dados()


def criar_admin():
    username = input("Usuario admin [admin]: ").strip() or "admin"
    email = input("Email [admin@kyly.com]: ").strip() or "admin@kyly.com"
    password = input("Senha: ").strip()
    if not password:
        print("Senha obrigatoria.")
        return

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Admin {username} criado com sucesso.")


def listar_usuarios():
    for user in User.objects.all():
        grupo = user.groups.first()
        print(
            f"- {user.username} | nome={user.get_full_name() or '-'} | "
            f"grupo={grupo.name if grupo else '-'} | admin={'sim' if user.is_staff else 'nao'}"
        )


def estatisticas():
    print(f"Produtos: {Produto.objects.count()}")
    print(f"Pedidos: {Pedido.objects.count()}")
    print(f"Itens de pedido: {ItemPedido.objects.count()}")
    print(f"Pickings: {Picking.objects.count()}")
    print(f"Erros: {Erro.objects.count()}")
    print(f"Usuarios: {User.objects.count()}")


def main_menu():
    while True:
        print("\nKYLY PICKING - MENU LOCAL")
        print("1. Popular banco de dados")
        print("2. Limpar tudo e recriar")
        print("3. Criar admin")
        print("4. Listar usuarios")
        print("5. Ver estatisticas")
        print("6. Sair")

        opcao = input("Escolha uma opcao: ").strip()
        if opcao == "1":
            popular_banco_dados()
        elif opcao == "2":
            limpar_tudo()
        elif opcao == "3":
            criar_admin()
        elif opcao == "4":
            listar_usuarios()
        elif opcao == "5":
            estatisticas()
        elif opcao == "6":
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        sys.exit(0)
