# Manual do Usuario - Kyly Picking

## 1. Objetivo da Solucao

O Kyly Picking e um sistema para apoiar a separacao de pedidos em ambiente logistico. Ele permite que operadores iniciem pedidos, sigam a rota de coleta, confirmem produtos por SKU, registrem erros, marquem itens em falta e acompanhem o progresso da operacao.

O sistema tambem possui uma area de gestor, usada para acompanhar indicadores, produtividade, erros e historico de pedidos.

## 2. Acesso ao Sistema

Para acessar o sistema, abra no navegador:

```text
http://localhost:8000/login/
```

Em ambiente de demonstracao, utilize:

- Operador: `operator / 123456`
- Gestor: `manager / 123456`

Tambem e possivel acessar por leitura de cracha quando a camera estiver disponivel:

- Cracha `OPERATOR`: entra como operador.
- Cracha `MANAGER`: entra como gestor.

## 3. Tela de Login

A tela de login permite entrar no sistema por usuario e senha ou por leitura de cracha.

### Login por usuario e senha

1. Digite o usuario no campo de matricula.
2. Digite a senha.
3. Clique em `Entrar`.

Se as credenciais estiverem corretas, o sistema direciona automaticamente para a tela correspondente ao perfil do usuario.

### Login por camera

1. Clique em `Abrir camera`.
2. Permita o acesso a camera no navegador.
3. Aponte a camera para o cracha.
4. Quando o codigo for reconhecido, o sistema preenche o usuario automaticamente.
5. Digite a senha, se necessario, e clique em `Entrar`.

Caso a camera nao funcione ou o navegador nao seja compativel, utilize o login manual.

## 4. Perfil Operador

O operador acessa a tela de operacao de picking. Essa e a tela principal para separacao de pedidos.

### 4.1 Tela Operacao de Picking

Nesta tela aparecem:

- pedido em andamento;
- percentual de progresso;
- distancia estimada;
- produto atual;
- SKU esperada;
- localizacao do item;
- quantidade a coletar;
- proximos itens da rota;
- pedidos disponiveis para iniciar.

Quando nenhum pedido estiver ativo, o operador deve escolher um pedido na lista `Pedidos disponiveis`.

### 4.2 Iniciar um Pedido

1. Localize a area `Pedidos disponiveis`.
2. Escolha o pedido desejado.
3. Clique em `Iniciar Picking`.
4. O sistema carrega o primeiro item da rota.

Se outro pedido ja estiver ativo para o operador, o sistema nao permite iniciar um novo ate que o atual seja finalizado.

### 4.3 Ler ou Digitar SKU

Na area `Escanear ou digitar SKU do item`, o operador pode confirmar o produto de duas formas.

#### Confirmacao por camera

1. Clique em `Abrir camera`.
2. Permita o acesso a camera.
3. Aponte para o codigo de barras ou QR Code do produto.
4. O sistema tenta reconhecer o codigo automaticamente.
5. Quando a SKU for lida, o sistema valida o item.

#### Confirmacao manual

1. Digite a SKU no campo de texto, por exemplo `SKU006`.
2. Clique em `Confirmar`.

Se a SKU estiver correta, o sistema confirma uma unidade, atualiza a quantidade coletada e emite som de sucesso.

Se a SKU estiver errada, o sistema exibe uma mensagem de erro, emite som de erro e nao confirma a coleta.

### 4.4 Quantidade Coletada

A tela mostra a quantidade no formato:

```text
quantidade coletada / quantidade total
```

Exemplo:

```text
1 / 3
```

Cada confirmacao correta aumenta a quantidade coletada. Quando a quantidade do item e atingida, o sistema avanca para a proxima coleta.

### 4.5 Pular Item

Use o botao `Pular item` quando o operador quiser deixar o item para depois.

Ao clicar:

1. O item volta para a fila.
2. O sistema carrega outro item pendente.
3. O pedido continua em andamento.

### 4.6 Relatar Erro

Use o botao `Relatar erro` quando houver algum problema durante a separacao.

Exemplos:

- embalagem danificada;
- endereco fisico divergente;
- produto diferente do esperado;
- problema operacional.

Passos:

1. Clique em `Relatar erro`.
2. Digite uma descricao do problema.
3. Confirme.

O erro fica registrado e pode ser consultado depois no historico.

### 4.7 Item em Falta

Use o botao `Item em falta` quando o produto nao for encontrado na localizacao indicada.

Ao clicar:

1. O sistema registra a ocorrencia.
2. O item fica marcado como falta.
3. Se existir uma localizacao alternativa, o sistema exibe uma nova sugestao.
4. O operador pode seguir a nova orientacao ou continuar a operacao conforme o processo definido.

### 4.8 Ler Instrucao

O botao `Ler instrucao` usa voz sintetizada do navegador para informar a proxima acao.

Ao clicar, o sistema fala:

- localizacao;
- quantidade restante;
- nome do produto.

Essa funcao depende do suporte do navegador a sintese de voz.

### 4.9 Comando por Voz

O botao `Comando por voz` ativa o reconhecimento de voz.

Quando ativo, o botao muda para `Ouvindo voz`. O operador pode falar comandos como:

- `confirmar`;
- `confirma`;
- `validar`;
- `pular`;
- `proximo`;
- `erro`;
- `problema`;
- `falta`;
- `nao achei`;
- `nao tem`;
- `acabou`.

O sistema exibe uma mensagem informando o comando reconhecido.

Observacoes:

- E necessario permitir o uso do microfone.
- O recurso funciona melhor em navegadores baseados em Chromium, como Chrome e Edge.
- Em ambiente com muito ruido, prefira os botoes da tela.

## 5. Perfil Gestor

O gestor acessa o dashboard gerencial e os historicos do sistema.

### 5.1 Dashboard do Gestor

A tela `Gestao de Operacoes` apresenta indicadores gerais da operacao.

O gestor consegue visualizar:

- total de pedidos;
- pedidos concluidos;
- pedidos em andamento;
- total de coletas;
- total de erros;
- tempo medio por picking;
- taxa de conclusao geral;
- erros por tipo;
- produtividade por operador;
- ultimos erros registrados.

Use esta tela para acompanhar a situacao geral da operacao e identificar gargalos.

### 5.2 Analise e Graficos

O dashboard possui areas visuais para facilitar a leitura dos dados.

Principais pontos:

- `Analise`: resume indicadores operacionais.
- `Erros por tipo`: mostra a distribuicao dos erros registrados.
- `Produtividade por operador`: compara desempenho entre operadores.
- `Ultimos erros registrados`: lista ocorrencias recentes para acompanhamento rapido.

## 6. Historico de Erros

A tela `Historico de Erros` lista os erros registrados no sistema.

Para acessar, use o menu `Erros`.

### 6.1 Informacoes exibidas

Cada registro pode exibir:

- pedido relacionado;
- operador;
- produto;
- tipo de erro;
- descricao;
- data e hora.

### 6.2 Filtro por tipo

O usuario pode filtrar os erros por tipo:

- SKU invalida;
- quantidade excessiva;
- produto nao encontrado;
- localizacao errada;
- item em falta;
- dano;
- outro.

Passos:

1. Selecione o tipo no campo de filtro.
2. Clique em `Aplicar`.

Para voltar a ver todos os erros, selecione `Todos` e aplique novamente.

### 6.3 Permissoes

- Gestores visualizam todos os erros.
- Operadores visualizam somente os erros relacionados ao proprio usuario.

## 7. Historico de Pedidos

A tela `Historico de Pedidos` permite consultar pedidos e seus status.

Para acessar, use o menu `Historico` ou `Pedidos`.

### 7.1 Informacoes exibidas

Cada pedido pode mostrar:

- numero do pedido;
- status;
- data de criacao;
- progresso;
- itens do pedido;
- quantidade de cada item;
- situacao da coleta.

### 7.2 Filtro por status

O usuario pode filtrar os pedidos por:

- pendente;
- em picking;
- concluido;
- cancelado.

Passos:

1. Selecione o status desejado.
2. Clique em `Aplicar`.

### 7.3 Permissoes

- Gestores visualizam todos os pedidos.
- Operadores visualizam somente os pedidos vinculados as proprias operacoes.

## 8. Menu e Navegacao

O sistema possui navegacao adaptada ao perfil.

### Operador

Opcoes principais:

- `Operacoes`: tela de picking.
- `Erros`: historico de erros.
- `Historico`: historico de pedidos.
- `Sair`: encerra a sessao.

### Gestor

Opcoes principais:

- `Dashboard`: painel gerencial.
- `Pedidos`: historico de pedidos.
- `Erros`: historico de erros.
- `Sair`: encerra a sessao.

Em telas menores, o menu aparece na parte inferior da tela.

## 9. Sons do Sistema

O sistema utiliza sons para auxiliar a operacao.

- Som de sucesso: SKU correta ou acao concluida.
- Som de erro: SKU incorreta, item em falta ou validacao recusada.

Se o navegador bloquear audio automatico, clique em algum botao da tela e tente novamente.

## 10. Uso em Celular ou Coletor

O sistema foi preparado para uso em telas pequenas.

Recomendacoes:

- use o celular ou coletor na orientacao vertical;
- mantenha boa iluminacao para leitura da camera;
- aproxime o codigo de barras da camera;
- evite reflexos no codigo;
- use Chrome ou Edge para melhor compatibilidade.

Para acessar pela rede local, o servidor deve ser iniciado com:

```bash
python manage.py runserver 0.0.0.0:8000
```

Depois, acesse no celular:

```text
http://SEU-IP-LOCAL:8000/login/
```

## 11. Mensagens Comuns

### Usuario ou senha incorretos

Verifique se o usuario e a senha foram digitados corretamente.

### Informe a SKU do item

O campo de SKU esta vazio. Digite ou leia um codigo antes de confirmar.

### SKU invalida ou item nao pertence ao pedido

A SKU informada nao corresponde ao item atual ou ao pedido em andamento.

### Quantidade ja atingida

O item ja teve toda a quantidade necessaria confirmada.

### Pedido nao esta ativo para este operador

O pedido pode nao ter sido iniciado por esse operador ou a sessao pode ter expirado.

### Permita o acesso ao microfone

O comando de voz precisa de permissao do navegador para usar o microfone.

### Libere a camera para escanear

A leitura por camera precisa de permissao do navegador.

## 12. Encerramento de Sessao

Para sair do sistema:

1. Clique em `Logout` ou `Sair`.
2. O sistema retorna para a tela de login.

Sempre saia do sistema ao finalizar o uso em equipamentos compartilhados.

## 13. Boas Praticas

- Confira sempre o nome do produto, SKU e localizacao antes de confirmar.
- Use a leitura por camera sempre que possivel para reduzir erros de digitacao.
- Registre erros com descricao clara.
- Use `Item em falta` apenas quando o produto realmente nao for encontrado.
- Em caso de duvida, nao confirme uma SKU diferente da indicada na tela.
- Gestores devem acompanhar periodicamente o dashboard e os historicos.

## 14. Resumo do Fluxo Operacional

1. Operador acessa o sistema.
2. Seleciona um pedido disponivel.
3. Inicia o picking.
4. Consulta produto, SKU, localizacao e quantidade.
5. Escaneia ou digita a SKU.
6. Confirma a coleta.
7. Repete o processo ate concluir todos os itens.
8. Registra erro ou falta quando necessario.
9. Gestor acompanha resultados no dashboard e historicos.
