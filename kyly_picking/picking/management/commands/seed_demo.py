from django.core.management.base import BaseCommand

from picking.fixtures import popular_banco_dados


class Command(BaseCommand):
    help = "Popula o banco com dados de demonstracao do Kyly Picking."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove os dados atuais antes de popular novamente.",
        )

    def handle(self, *args, **options):
        popular_banco_dados(limpar=options["limpar"])
        self.stdout.write(self.style.SUCCESS("Carga demo executada com sucesso."))
