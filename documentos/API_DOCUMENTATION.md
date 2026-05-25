# 📡 Kyly Picking - Documentação de API

API REST JSON para integração com sistemas externos.

## 🔑 Autenticação

A API usa **Django Session Authentication**. Você precisa fazer login primeiro:

```bash
# 1. Faça login
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=operator&password=123456" \
  -c cookies.txt

# 2. Use os cookies para requisições subsequentes
curl http://localhost:8000/api/dashboard/ \
  -b cookies.txt
```

Ou, se integrar com Token Auth (futura melhoria), use header:
```
Authorization: Bearer TOKEN
```

## 📋 Endpoints

### 🔐 Autenticação

#### POST `/login/`
Faz login no sistema.

**Parâmetros:**
```
username: string (obrigatório)
password: string (obrigatório)
```

**Resposta de sucesso (302 redirect):**
Redireciona para `/` (dashboard ou picking)

**Exemplo:**
```bash
curl -X POST http://localhost:8000/login/ \
  -d "username=operator&password=123456" \
  -c cookies.txt
```

---

#### GET `/logout/`
Faz logout do sistema.

**Resposta:**
Redireciona para `/login/`

**Exemplo:**
```bash
curl http://localhost:8000/logout/ -b cookies.txt
```

---

### 📊 Dashboard

#### GET `/api/dashboard/`
Retorna dados para o dashboard gerencial.

**Query Parameters:** Nenhum

**Resposta (JSON):**
```json
{
  "stats": {
    "total_pedidos": 5,
    "pedidos_concluidos": 3,
    "pedidos_em_picking": 1,
    "total_erros": 10,
    "total_operadores": 3,
    "taxa_erro": 2.5
  },
  "produtividade": [
    {
      "operador": "João Silva",
      "total_picking": 5,
      "conclusoes": 5,
      "taxa_conclusao": 100.0,
      "tempo_total_horas": 2.5
    }
  ],
  "erros_tipo": [
    {
      "tipo": "sku_invalida",
      "count": 4
    }
  ],
  "taxa_erro": 2.5,
  "tempo_medio": 1800
}
```

**Exemplo:**
```bash
curl http://localhost:8000/api/dashboard/ -b cookies.txt
```

---

### 🎯 Picking

#### POST `/picking/iniciar/`
Inicia uma sessão de picking para um pedido.

**Parâmetros (JSON):**
```json
{
  "numero_pedido": "PED00001"
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "Picking iniciado",
  "pedido_id": 1,
  "picking_id": 5
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/picking/iniciar/ \
  -H "Content-Type: application/json" \
  -d '{"numero_pedido": "PED00001"}' \
  -b cookies.txt
```

---

#### POST `/picking/validar-sku/`
Valida um SKU escaneado.

**Parâmetros (JSON):**
```json
{
  "item_id": 1,
  "sku_informado": "SKU001",
  "quantidade": 5
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "SKU válido!",
  "tipo": "sucesso",
  "item_completo": true,
  "progresso": 100,
  "proxima_coleta": {
    "item_id": 2,
    "produto_sku": "SKU002",
    "produto_nome": "Camiseta Preta",
    "quantidade": 3,
    "localizacao": "A-01-1A"
  }
}
```

**Erros possíveis:**
```json
{
  "sucesso": false,
  "mensagem": "SKU inválido",
  "tipo": "sku_invalida"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/picking/validar-sku/ \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "sku_informado": "SKU001", "quantidade": 5}' \
  -b cookies.txt
```

---

#### POST `/picking/reportar-erro/`
Registra um erro durante o picking.

**Parâmetros (JSON):**
```json
{
  "item_id": 1,
  "tipo_erro": "sku_invalida",
  "descricao": "SKU não corresponde ao item"
}
```

**Tipos de erro válidos:**
- `sku_invalida` - SKU não corresponde
- `quantidade_excessiva` - Quantidade não bate
- `produto_nao_encontrado` - Produto não achado na localização
- `localizacao_errada` - Localização incorreta
- `item_falta` - Item faltando
- `outro` - Outro problema

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "Erro registrado",
  "erro_id": 15
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/picking/reportar-erro/ \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 1,
    "tipo_erro": "sku_invalida",
    "descricao": "SKU não corresponde"
  }' \
  -b cookies.txt
```

---

#### POST `/picking/item-em-falta/`
Marca um item como faltando em estoque.

**Parâmetros (JSON):**
```json
{
  "item_id": 1,
  "descricao": "Não encontrado na localização indicada"
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "Item marcado como falta",
  "localizacao_alternativa": {
    "localizacao": "B-02-1B",
    "quantidade_disponivel": 8
  }
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/picking/item-em-falta/ \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 1,
    "descricao": "Não encontrado na localização"
  }' \
  -b cookies.txt
```

---

#### POST `/picking/proxima-coleta/`
Busca o próximo item otimizado para coleta.

**Parâmetros (JSON):**
```json
{
  "pedido_id": 1
}
```

**Resposta:**
```json
{
  "item_id": 2,
  "produto_sku": "SKU002",
  "produto_nome": "Camiseta Preta",
  "produto_cor": "Preto",
  "produto_tamanho": "M",
  "quantidade": 3,
  "quantidade_coletada": 0,
  "localizacao": "A-01-2A",
  "proximidade": "Próxima",
  "proximos_5": [
    {
      "item_id": 3,
      "produto_sku": "SKU003",
      "quantidade": 2,
      "localizacao": "A-01-3A"
    }
  ]
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/picking/proxima-coleta/ \
  -H "Content-Type: application/json" \
  -d '{"pedido_id": 1}' \
  -b cookies.txt
```

---

#### GET `/api/proxima-coleta/?pedido_id=1`
Versão GET do endpoint anterior (para simplificar integração).

**Query Parameters:**
```
pedido_id: integer (obrigatório) - ID do pedido
```

**Resposta:** Mesma do POST

**Exemplo:**
```bash
curl "http://localhost:8000/api/proxima-coleta/?pedido_id=1" \
  -b cookies.txt
```

---

### 📜 Histórico

#### GET `/historico/erros/?page=1&filtro=sku_invalida`
Lista histórico de erros (paginado).

**Query Parameters:**
```
page: integer (padrão: 1)
filtro: string (opcional) - Tipo de erro para filtrar
```

**Resposta (HTML):** Página HTML com tabela de erros
- Se for requisição AJAX, retorna tabela apenas
- Se for requisição normal, retorna página completa

**Exemplo:**
```bash
curl "http://localhost:8000/historico/erros/?page=1" -b cookies.txt
```

---

#### GET `/historico/pedidos/?page=1&filtro=concluido`
Lista histórico de pedidos (paginado).

**Query Parameters:**
```
page: integer (padrão: 1)
filtro: string (opcional) - Status do pedido: pendente, em_picking, concluido, cancelado
```

**Exemplo:**
```bash
curl "http://localhost:8000/historico/pedidos/?page=1&filtro=concluido" \
  -b cookies.txt
```

---

## 🔄 Fluxo Típico de Integração

```
1. LOGIN
   POST /login/
   ↓
2. INICIAR PICKING
   POST /picking/iniciar/
   ↓
3. VALIDAR SKUS (repetir)
   POST /picking/validar-sku/
   ↓
4. BUSCAR PRÓXIMO ITEM
   POST /picking/proxima-coleta/
   ou GET /api/proxima-coleta/
   ↓
5. REGISTRAR ERROS (se houver)
   POST /picking/reportar-erro/
   ou POST /picking/item-em-falta/
   ↓
6. REPETIR 3-5 até terminar pedido
   ↓
7. MONITORAR DASHBOARD (para gestores)
   GET /api/dashboard/
   ↓
8. LOGOUT
   GET /logout/
```

## 🛠️ Exemplos de Integração

### Python
```python
import requests
import json

BASE_URL = 'http://localhost:8000'
session = requests.Session()

# Login
response = session.post(f'{BASE_URL}/login/', data={
    'username': 'operator',
    'password': '123456'
})

# Iniciar picking
response = session.post(f'{BASE_URL}/picking/iniciar/', json={
    'numero_pedido': 'PED00001'
})
data = response.json()
pedido_id = data['pedido_id']

# Validar SKU
response = session.post(f'{BASE_URL}/picking/validar-sku/', json={
    'item_id': 1,
    'sku_informado': 'SKU001',
    'quantidade': 5
})
print(response.json())

# Próximo item
response = session.get(f'{BASE_URL}/api/proxima-coleta/', params={
    'pedido_id': pedido_id
})
print(response.json())

# Dashboard
response = session.get(f'{BASE_URL}/api/dashboard/')
stats = response.json()['stats']
print(f"Total pedidos: {stats['total_pedidos']}")
```

### JavaScript (Fetch)
```javascript
const BASE_URL = 'http://localhost:8000';

async function picking() {
  // Login
  await fetch(`${BASE_URL}/login/`, {
    method: 'POST',
    body: new URLSearchParams({
      username: 'operator',
      password: '123456'
    }),
    credentials: 'include'
  });

  // Iniciar picking
  const initRes = await fetch(`${BASE_URL}/picking/iniciar/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ numero_pedido: 'PED00001' }),
    credentials: 'include'
  });
  const initData = await initRes.json();

  // Validar SKU
  const validRes = await fetch(`${BASE_URL}/picking/validar-sku/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      item_id: 1,
      sku_informado: 'SKU001',
      quantidade: 5
    }),
    credentials: 'include'
  });
  const validData = await validRes.json();
  console.log(validData);
}

picking();
```

### cURL
```bash
# Login
curl -X POST http://localhost:8000/login/ \
  -d "username=operator&password=123456" \
  -c cookies.txt

# Iniciar picking
curl -X POST http://localhost:8000/picking/iniciar/ \
  -H "Content-Type: application/json" \
  -d '{"numero_pedido":"PED00001"}' \
  -b cookies.txt

# Validar SKU
curl -X POST http://localhost:8000/picking/validar-sku/ \
  -H "Content-Type: application/json" \
  -d '{"item_id":1,"sku_informado":"SKU001","quantidade":5}' \
  -b cookies.txt

# Dashboard
curl http://localhost:8000/api/dashboard/ -b cookies.txt | python -m json.tool
```

## 🚀 Futuros Endpoints

- [ ] `GET /api/produtos/` - Listar produtos
- [ ] `GET /api/localizacoes/` - Listar localizações
- [ ] `GET /api/pedidos/` - Listar pedidos
- [ ] `POST /api/pedidos/` - Criar pedido
- [ ] `GET /api/operador/{id}/` - Dados do operador
- [ ] `GET /api/estatisticas/` - Estatísticas avançadas
- [ ] WebSocket para tempo real

## 📝 Status Codes

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado |
| 302 | Redirect - Redirecionamento (login) |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Não encontrado |
| 500 | Internal Server Error - Erro do servidor |

## 🔒 CSRF Token

Para requisições POST sem AJAX automático, inclua o token CSRF:

```html
<!-- HTML Form -->
<form method="post" action="/picking/validar-sku/">
  {% csrf_token %}
  <input type="hidden" name="item_id" value="1">
  <input type="text" name="sku_informado" placeholder="SKU">
  <button>Validar</button>
</form>
```

Ou em JavaScript:
```javascript
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/picking/validar-sku/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrftoken
  },
  body: JSON.stringify({...})
});
```

---