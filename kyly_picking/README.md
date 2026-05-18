# Kyly Picking

Sistema de picking inteligente para operacoes logisticas industriais, desenvolvido com Django no backend e HTML, CSS e JavaScript puro no frontend.

## Principais funcionalidades

- autenticacao por perfil com operador e gestor;
- tela de picking com validacao de SKU, progresso e ocorrencias;
- dashboard gerencial com produtividade, erros e graficos em canvas;
- sugestao de localizacao alternativa para item em falta;
- suporte basico a voz com Web Speech API;
- arquitetura preparada para SQLite no inicio e PostgreSQL no futuro.

## Estrutura do projeto

```text
kyly_picking/
|-- manage.py
|-- db.sqlite3
|-- .env.example
|-- kyly_picking/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
`-- picking/
    |-- admin.py
    |-- fixtures.py
    |-- forms.py
    |-- models.py
    |-- services.py
    |-- urls.py
    |-- views.py
    |-- management/commands/seed_demo.py
    |-- migrations/
    |-- static/
    |   |-- css/style.css
    |   `-- js/
    |       |-- picking.js
    |       |-- speech.js
    |       `-- dashboard.js
    |-- templates/
    |   |-- base.html
    |   |-- login.html
    |   |-- picking.html
    |   |-- dashboard_gestor.html
    |   |-- historico_erros.html
    |   `-- historico_pedidos.html
    |-- templatetags/picking_extras.py
    `-- tests/
        |-- test_services.py
        `-- test_views.py
```

## Como executar

```bash
cd kyly_picking
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo --limpar
python manage.py runserver
```

Abra `http://localhost:8000/login/`.

## Credenciais demo

- Operador: `operator / 123456`
- Gestor: `manager / 123456`

## Variaveis de ambiente

Copie `.env.example` para `.env` se quiser customizar:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_ENGINE=sqlite` ou `postgres`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`

## Testes

```bash
python manage.py test
```

## Melhorias futuras

- algoritmo de rota baseado em grafos;
- regras avancadas de prioridade por pedido;
- CRUD operacional completo para produtos, pedidos e localizacoes;
- exportacao de relatorios;
- atualizacao em tempo real via WebSocket;
- integracao com ERP e leitores fisicos.
