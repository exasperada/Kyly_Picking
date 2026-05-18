"""
URL Configuration para a app Picking.
Define todas as rotas do sistema.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/scan/login/', views.api_scan_login_code, name='api_scan_login_code'),

    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Picking
    path('picking/', views.tela_picking, name='tela_picking'),

    # Picking - Operações
    path('picking/iniciar/', views.iniciar_picking, name='iniciar_picking'),
    path('picking/validar-sku/', views.validar_sku, name='validar_sku'),
    path('picking/reportar-erro/', views.reportar_erro, name='reportar_erro'),
    path('picking/item-em-falta/', views.item_em_falta, name='item_em_falta'),
    path('picking/proxima-coleta/', views.proxima_coleta, name='proxima_coleta'),
    path('picking/pular-item/', views.pular_item, name='pular_item'),
    path('api/scan/item/', views.api_scan_item_code, name='api_scan_item_code'),

    # Histórico
    path('historico/erros/', views.historico_erros, name='historico_erros'),
    path('historico/pedidos/', views.historico_pedidos, name='historico_pedidos'),

    # API
    path('api/dashboard/', views.api_dados_dashboard, name='api_dashboard'),
    path('api/proxima-coleta/', views.api_proxima_coleta, name='api_proxima_coleta'),
]
