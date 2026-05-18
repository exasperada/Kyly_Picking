"""
Models para o sistema Kyly Picking.
Define todas as entidades e relacionamentos do sistema logístico.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Produto(models.Model):
    """
    Modelo de Produto.
    Representa os itens que serão coletados no estoque.
    """
    nome = models.CharField(max_length=255, help_text="Nome do produto")
    sku = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="SKU único do produto"
    )
    cor = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Cor do produto"
    )
    tamanho = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Tamanho do produto"
    )
    descricao = models.TextField(blank=True, help_text="Descrição detalhada")
    ativo = models.BooleanField(default=True, help_text="Se o produto está ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sku']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.sku} - {self.nome}"


class Localizacao(models.Model):
    """
    Modelo de Localização no estoque.
    Define a posição exata do produto: corredor, seção e nível.
    """
    corredor = models.CharField(
        max_length=10, 
        help_text="Ex: A, B, C, D..."
    )
    secao = models.CharField(
        max_length=10, 
        help_text="Ex: 01, 02, 03..."
    )
    nivel = models.CharField(
        max_length=10, 
        help_text="Ex: 1A, 2B, 3C..."
    )
    descricao = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Descrição da localização"
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('corredor', 'secao', 'nivel')
        ordering = ['corredor', 'secao', 'nivel']
        verbose_name = 'Localização'
        verbose_name_plural = 'Localizações'

    def __str__(self):
        return f"{self.corredor}-{self.secao}-{self.nivel}"

    def endereco_completo(self):
        """Retorna o endereço completo da localização"""
        return f"Corredor {self.corredor} Seção {self.secao} Nível {self.nivel}"


class ProdutoLocalizacao(models.Model):
    """
    Modelo de relacionamento entre Produto e Localização.
    Armazena a quantidade de produtos em cada localização.
    """
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='localizacoes'
    )
    localizacao = models.ForeignKey(
        Localizacao,
        on_delete=models.CASCADE,
        related_name='produtos'
    )
    quantidade = models.IntegerField(
        default=0,
        help_text="Quantidade disponível"
    )
    quantidade_reservada = models.IntegerField(
        default=0,
        help_text="Quantidade reservada em pedidos"
    )
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('produto', 'localizacao')
        verbose_name = 'Produto por Localização'
        verbose_name_plural = 'Produtos por Localização'

    def __str__(self):
        return f"{self.produto.sku} em {self.localizacao}"

    def quantidade_disponivel(self):
        """Retorna quantidade realmente disponível"""
        return max(0, self.quantidade - self.quantidade_reservada)


class Pedido(models.Model):
    """
    Modelo de Pedido.
    Representa um conjunto de itens a serem coletados.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_picking', 'Em Picking'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    numero_pedido = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Número único do pedido"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido {self.numero_pedido}"

    def quantidade_itens_total(self):
        """Retorna a quantidade total de itens no pedido"""
        return sum(
            item.quantidade for item in self.itens.all()
        )

    def quantidade_coletada(self):
        """Retorna a quantidade total coletada"""
        return sum(
            item.quantidade_coletada for item in self.itens.all()
        )

    def percentual_progresso(self):
        """Calcula o percentual de progresso do picking"""
        total = self.quantidade_itens_total()
        if total == 0:
            return 0
        coletada = self.quantidade_coletada()
        return int((coletada / total) * 100)


class ItemPedido(models.Model):
    """
    Modelo de Item do Pedido.
    Representa cada produto que precisa ser coletado.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_picking', 'Em Picking'),
        ('confirmado', 'Confirmado'),
        ('falta', 'Em Falta'),
        ('cancelado', 'Cancelado'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )
    localizacao = models.ForeignKey(
        Localizacao,
        on_delete=models.SET_NULL,
        null=True
    )
    quantidade = models.IntegerField(help_text="Quantidade necessária")
    quantidade_coletada = models.IntegerField(
        default=0,
        help_text="Quantidade já coletada"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pedido', 'produto']
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.produto.sku}"

    def faltando_coletar(self):
        """Retorna a quantidade que ainda falta coletar"""
        return max(0, self.quantidade - self.quantidade_coletada)

    def percentual_coletado(self):
        """Retorna o percentual coletado"""
        if self.quantidade == 0:
            return 0
        return int((self.quantidade_coletada / self.quantidade) * 100)


class Picking(models.Model):
    """
    Modelo de Sessão de Picking.
    Rastreia a atividade de um operador durante o picking de um pedido.
    """
    STATUS_CHOICES = [
        ('iniciado', 'Iniciado'),
        ('em_progresso', 'Em Progresso'),
        ('pausado', 'Pausado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Operador responsável"
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='pickings'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='iniciado'
    )
    inicio = models.DateTimeField(auto_now_add=True)
    fim = models.DateTimeField(null=True, blank=True)
    duracao_segundos = models.IntegerField(default=0)

    class Meta:
        ordering = ['-inicio']
        verbose_name = 'Picking'
        verbose_name_plural = 'Pickings'

    def __str__(self):
        return f"{self.usuario.username} - {self.pedido.numero_pedido}"

    def calcular_duracao(self):
        """Calcula a duração do picking em segundos"""
        if self.fim:
            duracao = self.fim - self.inicio
            return int(duracao.total_seconds())
        return 0


class Erro(models.Model):
    """
    Modelo de Erro/Incidente.
    Registra problemas durante o picking para análise gerencial.
    """
    TIPO_CHOICES = [
        ('sku_invalida', 'SKU Inválida'),
        ('quantidade_excessiva', 'Quantidade Excessiva'),
        ('produto_nao_encontrado', 'Produto Não Encontrado'),
        ('localizacao_errada', 'Localização Errada'),
        ('item_falta', 'Item em Falta'),
        ('dano', 'Produto Danificado'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='erros'
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='erros'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo do erro"
    )
    descricao = models.TextField(help_text="Descrição detalhada do erro")
    data_hora = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False)
    resolucao = models.TextField(blank=True, help_text="Como foi resolvido")

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Erro'
        verbose_name_plural = 'Erros'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario.username} - {self.data_hora}"


class TentativaValidacao(models.Model):
    """
    Modelo para registrar tentativas de validação de SKU.
    Útil para auditoria e análise de produtividade.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tentativas_validacao'
    )
    item_pedido = models.ForeignKey(
        ItemPedido,
        on_delete=models.CASCADE,
        related_name='tentativas'
    )
    sku_informado = models.CharField(max_length=50)
    resultado = models.CharField(
        max_length=50,
        choices=[
            ('sucesso', 'Sucesso'),
            ('sku_invalida', 'SKU Inválida'),
            ('quantidade_atingida', 'Quantidade Atingida'),
            ('outro', 'Outro'),
        ]
    )
    mensagem = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Tentativa de Validação'
        verbose_name_plural = 'Tentativas de Validação'

    def __str__(self):
        return f"{self.usuario.username} - {self.sku_informado} - {self.resultado}"
