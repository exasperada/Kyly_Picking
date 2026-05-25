# Quick Start - Kyly Picking

## 1. Instale dependencias

```bash
cd kyly_picking
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Prepare o banco

```bash
python manage.py migrate
python manage.py seed_demo --limpar
```

## 3. Rode o sistema

```bash
python manage.py runserver
```

Acesse `http://localhost:8000/login/`.

## 4. Credenciais demo

- Operador: `operator / 123456`
- Gestor: `manager / 123456`
- Login por camera:
  - cracha `OPERATOR` entra como operador
  - cracha `MANAGER` entra como gestor

## 5. Dados de teste importantes

O seed cria automaticamente:

- 5 pedidos demo: `PED00001` ate `PED00005`
- 10 produtos com SKU:
  - `SKU001` Camiseta Basica Branco
  - `SKU002` Camiseta Basica Preto
  - `SKU003` Calca Jeans Azul
  - `SKU004` Jaqueta Inverno Preto
  - `SKU005` Sapato Casual Marrom
  - `SKU006` Bolsa de Couro Preto
  - `SKU007` Cinto Casual Marrom
  - `SKU008` Meias Algodao Branco
  - `SKU009` Lenco Seda Vermelho
  - `SKU010` Gravata Formal Azul
- localizacoes em corredores `A` a `E`, secoes `01` a `05`, niveis `1A`, `1B` e `2A`
- codigos escaneaveis gerados automaticamente em:
  - `crachás/`
  - `códigos de barra/`

Observacao importante:

- os 3 primeiros pedidos podem aparecer como concluidos no historico por causa da massa demo;
- para testar o picking operacional, normalmente use os pedidos restantes listados em `Pedidos disponiveis` na tela do operador.

## 6. Roteiro completo para testar o sistema

### Fluxo do operador

1. Entre com `operator / 123456`.
2. Se quiser testar o scanner do login, abra um dos arquivos da pasta `crachás` em outro celular, monitor ou impressao e toque em `Abrir camera`.
3. O login vai ler automaticamente `OPERATOR` ou `MANAGER`.
4. Na tela `Operacao de picking`, veja a lista `Pedidos disponiveis`.
5. Toque em `Iniciar pedido`.
6. O sistema vai abrir o item atual com:
   - nome do produto
   - SKU esperada
   - localizacao
   - quantidade
7. Para teste por camera, abra a imagem correspondente na pasta `códigos de barra`.
8. Toque em `Abrir camera` na area do scanner de SKU e aponte para o codigo.
9. Para teste manual, tambem e possivel digitar a SKU exata no campo.
10. Resultado esperado:
   - mensagem `Produto confirmado`
   - beep de sucesso
   - progresso atualizado
11. Quando o item completar, a tela avanca para a proxima coleta.

### Teste de SKU incorreta

1. Inicie um pedido.
2. Veja qual SKU a tela pede.
3. Digite uma SKU diferente, por exemplo:
   - se a tela pedir `SKU004`, digite `SKU001`
   - ou digite uma SKU inexistente, como `SKU999`
4. Resultado esperado:
   - `Item nao pertence ao pedido` ou `SKU invalida`
   - beep de erro
   - item nao confirmado

### Teste de quantidade atingida

1. Complete um item ate atingir a quantidade total.
2. Digite a mesma SKU novamente para o mesmo item, antes de avancar ou ao recarregar a operacao.
3. Resultado esperado:
   - `Quantidade ja atingida`
   - beep de erro

### Teste de item em falta

1. Com um item ativo, toque em `Item em falta`.
2. Resultado esperado:
   - registro de ocorrencia
   - mensagem com `Nova sugestao` quando existir outra localizacao
   - beep de erro

### Teste de reportar erro

1. Com um item ativo, toque em `Reportar erro`.
2. Digite qualquer descricao, por exemplo:
   - `Embalagem danificada`
   - `Endereco fisico divergente`
3. Resultado esperado:
   - erro salvo no sistema
   - feedback visual na tela

### Teste de voz

1. Com um item ativo, toque em `Ler instrucao`.
2. Resultado esperado:
   - o navegador fala corredor, secao, nivel e quantidade
3. Toque em `Comando de voz`.
4. Tente comandos simples:
   - `confirmar`
   - `pular`
   - `erro`
   - `falta`

### Fluxo do gestor

1. Saia do operador.
2. Entre com `manager / 123456`.
3. Verifique no dashboard:
   - total de pedidos
   - total de coletas
   - total de erros
   - erros por operador
   - produtividade por operador
4. Abra `Historico de erros`.
5. Confirme se aparecem os erros gerados no teste do operador.
6. Abra `Historico de pedidos`.
7. Confirme status, progresso e itens de cada pedido.

## 7. Teste em celular

O sistema foi ajustado para uso mobile:

- cards empilham em uma coluna;
- botoes ficam grandes para toque;
- barra superior se reorganiza em telas pequenas;
- campos de leitura e validacao ficam em largura total;
- a tela de picking funciona melhor em orientacao retrato.
- o fluxo do operador foi desenhado para largura de coletor mesmo em monitor grande.

Para testar no celular da rede local:

```bash
python manage.py runserver 0.0.0.0:8000
```

Depois abra no celular:

```text
http://SEU-IP-LOCAL:8000/login/
```

Exemplo:

```text
http://192.168.0.15:8000/login/
```

## 8. Sons de beep

O frontend tenta tocar estes arquivos:

- `/static/audio/bipe.mp3`
- `/static/audio/bipeerro.mp3`

Comportamento atual:

- sucesso na leitura e confirmacao usa `bipe.mp3`
- erro de codigo ou validacao usa `bipeerro.mp3`
- se esses arquivos ainda nao existirem, o sistema usa um beep sintetico automatico no navegador

Se voce quiser substituir pelo som real do seu coletor, basta colocar os arquivos:

- `picking/static/audio/bipe.mp3`
- `picking/static/audio/bipeerro.mp3`

## 9. Leitura por camera

O sistema usa a API nativa do navegador para leitura ao vivo:

- login: leitura de cracha via camera
- picking: leitura de codigo de barras da SKU via camera

Melhor compatibilidade:

- Chrome para Android
- Edge Chromium
- navegadores mobile baseados em Chromium

Se o navegador nao suportar `BarcodeDetector`, o sistema continua com digitacao manual.

## 10. Arquivos de teste visuais

Pastas criadas no projeto:

- `crachás/`
- `códigos de barra/`

Arquivos principais:

- `crachás/cracha_operator.svg`
- `crachás/cracha_manager.svg`
- `códigos de barra/SKU001.svg` ate `SKU010.svg`

Voce pode:

- abrir os SVGs no navegador
- mostrar em outro monitor
- abrir no celular secundario
- imprimir para testar o coletor

## 11. Comandos uteis

```bash
python manage.py createsuperuser
python manage.py seed_demo
python manage_commands.py
python manage.py test
python manage.py check
python generate_scannable_assets.py
```

## 12. Checklist final de validacao

- login do operador funcionando
- login do gestor funcionando
- scanner de cracha pedindo acesso a camera
- scanner de cracha reconhecendo `OPERATOR` e `MANAGER`
- pedido iniciando pela tela do operador
- SKU correta confirmando com beep
- SKU incorreta disparando beep de erro
- scanner de SKU pedindo acesso a camera
- scanner de SKU lendo os arquivos da pasta `códigos de barra`
- item em falta registrando ocorrencia
- erro manual aparecendo no historico
- dashboard do gestor refletindo os dados
- tela usavel em celular
