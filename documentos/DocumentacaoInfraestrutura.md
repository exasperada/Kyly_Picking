# Documentacao de Infraestrutura - Kyly Picking

## 1. Objetivo

Este documento descreve os requisitos minimos de infraestrutura para uso, operacao e hospedagem do sistema Kyly Picking.

A documentacao contempla:

- requisitos de hardware por tipo de usuario;
- infraestrutura recomendada para operador e gestor;
- requisitos de rede;
- servidores necessarios para hospedagem;
- configuracao minima para ambiente local, homologacao e producao;
- observacoes sobre camera, microfone, audio e leitura de codigos.

## 2. Tipos de Usuario

O sistema possui dois perfis principais:

- Operador: usuario responsavel pela execucao do picking, leitura de SKU, confirmacao de produtos, registro de erros e itens em falta.
- Gestor: usuario responsavel pelo acompanhamento de indicadores, dashboard, produtividade, historico de pedidos e historico de erros.

Cada perfil possui necessidades diferentes de hardware e infraestrutura.

## 3. Infraestrutura do Usuario Operador

O operador utiliza o sistema diretamente na area operacional, normalmente em celular, coletor, tablet ou computador proximo ao estoque.

### 3.1 Dispositivo recomendado

Recomendado:

- coletor de dados Android;
- smartphone Android;
- tablet Android;
- computador ou notebook com camera, quando usado em bancada.

O uso em celular ou coletor e o mais indicado, pois o sistema foi preparado para telas menores e operacao por toque.

### 3.2 Requisito minimo de hardware do operador

Configuracao minima:

- processador: dual-core 1.8 GHz ou superior;
- memoria RAM: 3 GB ou superior;
- armazenamento livre: 500 MB;
- tela: 5 polegadas ou superior;
- resolucao minima: 720 x 1280;
- camera traseira: 8 MP ou superior;
- conexao Wi-Fi ou rede movel estavel;
- alto-falante funcional para sons de confirmacao e erro;
- microfone funcional para comandos de voz, caso esse recurso seja utilizado.

Configuracao recomendada:

- processador: octa-core 2.0 GHz ou superior;
- memoria RAM: 4 GB ou superior;
- armazenamento livre: 1 GB;
- camera traseira com foco automatico;
- tela de 6 polegadas ou superior;
- bateria em bom estado para uso continuo;
- capa de protecao para ambiente logistico.

### 3.3 Navegador do operador

Recomendado:

- Google Chrome atualizado;
- Microsoft Edge atualizado;
- navegadores Android baseados em Chromium.

Recursos necessarios no navegador:

- suporte a camera via `getUserMedia`;
- suporte a JavaScript;
- suporte a audio no navegador;
- suporte a microfone, se comandos de voz forem utilizados;
- permissao para acessar camera e microfone.

Observacao: a leitura por camera pode variar conforme navegador, iluminacao, qualidade da camera e tipo do codigo utilizado.

### 3.4 Infraestrutura fisica do operador

Recomendado para a area operacional:

- boa cobertura Wi-Fi nos corredores de estoque;
- iluminacao adequada para leitura de codigos;
- pontos de recarga para coletores ou celulares;
- dispositivos com protecao fisica contra quedas;
- volume de audio audivel no ambiente;
- codigos de barras ou QR Codes impressos com boa qualidade.

### 3.5 Rede para operador

Requisitos minimos:

- conexao com o servidor do sistema;
- latencia baixa e estavel;
- acesso HTTP/HTTPS ao endereco do sistema;
- permissao de trafego na porta configurada da aplicacao.

Em ambiente local de teste, a porta padrao utilizada e:

```text
8000
```

Em producao, recomenda-se uso de HTTPS na porta:

```text
443
```

## 4. Infraestrutura do Usuario Gestor

O gestor utiliza o sistema para acompanhar dashboard, historicos e indicadores.

### 4.1 Dispositivo recomendado

Recomendado:

- computador desktop;
- notebook;
- tablet com tela grande.

O dashboard pode ser acessado em celular, mas a experiencia e melhor em telas maiores.

### 4.2 Requisito minimo de hardware do gestor

Configuracao minima:

- processador: dual-core 1.8 GHz ou superior;
- memoria RAM: 4 GB ou superior;
- armazenamento livre: 500 MB;
- tela: 10 polegadas ou superior;
- resolucao minima: 1366 x 768;
- conexao de rede estavel.

Configuracao recomendada:

- processador: quad-core 2.0 GHz ou superior;
- memoria RAM: 8 GB ou superior;
- tela: 14 polegadas ou superior;
- resolucao Full HD, 1920 x 1080;
- navegador atualizado.

### 4.3 Navegador do gestor

Recomendado:

- Google Chrome atualizado;
- Microsoft Edge atualizado;
- Mozilla Firefox atualizado.

Recursos necessarios:

- suporte a JavaScript;
- suporte a Canvas para exibicao de graficos;
- cookies habilitados para sessao de usuario;
- acesso ao endereco do servidor.

## 5. Servidor de Aplicacao

O Kyly Picking e uma aplicacao web desenvolvida com Django. Para hospedagem, e necessario um servidor capaz de executar Python e servir a aplicacao web.

### 5.1 Ambiente de desenvolvimento local

Para testes locais, pode ser usado o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

Requisitos minimos para desenvolvimento:

- sistema operacional: Windows, Linux ou macOS;
- Python 3.12 ou compativel;
- memoria RAM: 4 GB;
- armazenamento livre: 2 GB;
- SQLite;
- navegador atualizado.

Esse modo e indicado apenas para desenvolvimento, apresentacao academica ou testes controlados.

### 5.2 Servidor de homologacao

Para homologacao, recomenda-se um ambiente mais proximo da producao.

Configuracao minima:

- 2 vCPU;
- 4 GB de RAM;
- 20 GB de armazenamento SSD;
- sistema operacional Linux ou Windows Server;
- Python instalado;
- banco SQLite ou PostgreSQL;
- acesso restrito a usuarios de teste.

Configuracao recomendada:

- 2 vCPU ou mais;
- 8 GB de RAM;
- 40 GB de armazenamento SSD;
- PostgreSQL;
- HTTPS configurado;
- rotina de backup.

### 5.3 Servidor de producao

Para producao, recomenda-se separar a aplicacao, o banco de dados e os arquivos estaticos conforme a necessidade de escala.

Configuracao minima para pequeno uso:

- 2 vCPU;
- 4 GB de RAM;
- 40 GB de armazenamento SSD;
- sistema operacional Linux Server;
- Python 3.12;
- servidor WSGI, como Gunicorn ou uWSGI;
- servidor web reverso, como Nginx ou Apache;
- banco PostgreSQL;
- HTTPS.

Configuracao recomendada:

- 4 vCPU;
- 8 GB de RAM;
- 80 GB ou mais de armazenamento SSD;
- PostgreSQL em servidor separado ou servico gerenciado;
- Nginx como proxy reverso;
- certificado SSL/TLS;
- monitoramento de aplicacao;
- backup diario;
- politica de logs;
- controle de acesso por rede.

## 6. Banco de Dados

O projeto esta preparado para uso inicial com SQLite e evolucao para PostgreSQL.

### 6.1 SQLite

Indicado para:

- desenvolvimento local;
- demonstracoes;
- testes pequenos;
- apresentacao academica.

Vantagens:

- simples de configurar;
- nao exige servidor separado;
- arquivo unico no projeto.

Limitacoes:

- nao recomendado para muitos usuarios simultaneos;
- menor robustez para producao;
- backup depende da copia correta do arquivo do banco.

### 6.2 PostgreSQL

Indicado para:

- homologacao;
- producao;
- multiplos usuarios;
- maior volume de dados;
- maior confiabilidade.

Requisitos minimos para servidor de banco:

- 2 vCPU;
- 4 GB de RAM;
- 40 GB de armazenamento SSD;
- backup automatico;
- acesso restrito ao servidor da aplicacao.

Requisitos recomendados:

- 4 vCPU;
- 8 GB de RAM;
- armazenamento SSD com expansao;
- backups diarios;
- monitoramento de uso de disco, CPU e memoria;
- politica de retencao de backups.

## 7. Arquivos Estaticos e Midia

O sistema utiliza arquivos estaticos como:

- CSS;
- JavaScript;
- audios de beep;
- imagens e arquivos de apoio.

Em desenvolvimento, esses arquivos podem ser servidos pelo Django.

Em producao, recomenda-se servir estaticos pelo Nginx, Apache ou servico equivalente, pois isso melhora desempenho e estabilidade.

Diretorios importantes:

```text
picking/static/
staticfiles/
```

Antes de publicar em producao, deve-se executar:

```bash
python manage.py collectstatic
```

## 8. Rede e Conectividade

### 8.1 Requisitos minimos de rede

- rede local ou internet com acesso ao servidor;
- portas liberadas conforme ambiente;
- estabilidade suficiente para requisicoes frequentes;
- baixa perda de pacote.

### 8.2 Portas comuns

Desenvolvimento:

```text
8000
```

Producao HTTP:

```text
80
```

Producao HTTPS:

```text
443
```

Banco PostgreSQL, quando separado:

```text
5432
```

A porta do banco nao deve ficar aberta publicamente. Ela deve aceitar conexoes apenas do servidor da aplicacao ou da rede interna autorizada.

### 8.3 Wi-Fi operacional

Para uso com operadores em estoque, recomenda-se:

- cobertura em todos os corredores;
- sinal estavel nas areas de picking;
- uso de rede corporativa protegida;
- baixa interferencia;
- roteadores ou access points dimensionados para a quantidade de dispositivos;
- teste real de conectividade nos pontos de coleta.

## 9. Seguranca

Recomendacoes minimas:

- utilizar HTTPS em producao;
- manter `SECRET_KEY` fora do codigo-fonte;
- configurar `DEBUG=False` em producao;
- restringir `ALLOWED_HOSTS`;
- utilizar senhas fortes;
- limitar acesso ao banco de dados;
- manter servidor e dependencias atualizados;
- realizar backups periodicos;
- controlar usuarios e perfis de acesso.

Variaveis de ambiente relevantes:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_ENGINE
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
SESSION_COOKIE_SECURE
```

## 10. Backup e Recuperacao

### 10.1 Ambiente com SQLite

Realizar backup do arquivo:

```text
db.sqlite3
```

Recomendacoes:

- parar a aplicacao antes de copiar o arquivo;
- armazenar backup fora do servidor principal;
- manter historico de backups.

### 10.2 Ambiente com PostgreSQL

Recomendacoes:

- backup diario;
- retencao minima de 7 a 30 dias;
- teste periodico de restauracao;
- armazenamento em local seguro;
- monitoramento de falhas no backup.

## 11. Monitoramento

Em producao, recomenda-se monitorar:

- disponibilidade da aplicacao;
- uso de CPU;
- uso de memoria;
- uso de disco;
- tempo de resposta;
- erros HTTP;
- logs da aplicacao;
- conexoes com banco de dados;
- crescimento do banco.

Para ambientes simples, a verificacao pode ser manual. Para ambientes produtivos, recomenda-se uso de ferramentas de monitoramento.

## 12. Escalabilidade

Para poucos usuarios, uma unica maquina pode hospedar aplicacao e banco de dados.

Para aumento de uso, recomenda-se:

- separar banco de dados em servidor proprio;
- usar Nginx como proxy reverso;
- executar a aplicacao com Gunicorn ou uWSGI;
- configurar multiplos workers;
- usar armazenamento SSD;
- monitorar gargalos antes de ampliar recursos.

## 13. Infraestrutura Minima por Cenario

### 13.1 Demonstracao local

- 1 computador com Python;
- SQLite;
- navegador atualizado;
- execucao via `python manage.py runserver`;
- acesso em `http://localhost:8000/login/`.

### 13.2 Pequena operacao interna

- 1 servidor com 2 vCPU e 4 GB RAM;
- PostgreSQL ou SQLite, conforme criticidade;
- rede Wi-Fi estavel;
- operadores em celulares ou coletores Android;
- gestores em computadores ou notebooks;
- backup periodico.

### 13.3 Producao recomendada

- servidor de aplicacao com 4 vCPU e 8 GB RAM;
- PostgreSQL;
- Nginx ou Apache;
- HTTPS;
- backups diarios;
- monitoramento;
- rede Wi-Fi dimensionada para a operacao;
- dispositivos de operador com camera e boa bateria.

## 14. Resumo dos Requisitos por Perfil

| Perfil | Dispositivo minimo | Dispositivo recomendado | Recursos importantes |
| --- | --- | --- | --- |
| Operador | Smartphone/coletor com 3 GB RAM, camera 8 MP e tela 720p | Coletor Android ou smartphone com 4 GB RAM, foco automatico e boa bateria | Camera, audio, microfone, Wi-Fi estavel |
| Gestor | Notebook/computador com 4 GB RAM e tela 1366 x 768 | Notebook/computador com 8 GB RAM e tela Full HD | Navegador moderno, graficos, acesso ao dashboard |
| Servidor local | Computador com 4 GB RAM | Computador com 8 GB RAM | Python, SQLite, Django |
| Servidor producao | 2 vCPU, 4 GB RAM, SSD | 4 vCPU, 8 GB RAM, SSD, PostgreSQL | HTTPS, backup, monitoramento, proxy reverso |

## 15. Consideracoes Finais

O Kyly Picking pode ser executado de forma simples em ambiente local para testes e demonstracoes. Para uso real em operacao logistica, recomenda-se infraestrutura com servidor dedicado, rede Wi-Fi estavel, dispositivos moveis adequados e banco de dados robusto.

A qualidade da experiencia do operador depende principalmente de:

- estabilidade da rede;
- qualidade da camera;
- iluminacao do ambiente;
- desempenho do dispositivo;
- permissao correta de camera, microfone e audio no navegador.

Para producao, o uso de HTTPS, backup e monitoramento e essencial para garantir seguranca e continuidade da operacao.
