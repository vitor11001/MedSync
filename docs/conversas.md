# Conversas do Projeto

## 2026-03-21

### Contexto inicial

- O projeto tem como objetivo criar um sistema medico.
- Neste momento, vamos apenas conversar e registrar as decisoes.

### Primeiro escopo definido

Comecar pequeno com o fluxo de marcacao da consulta diaria.

- O paciente chega na clinica.
- Os dados do paciente sao informados.
- A consulta e marcada para o medico.
- O valor da consulta paga deve ser registrado.
- A forma de pagamento deve ser registrada.
- O tipo de consulta deve ser registrado.

### Proximo ponto natural da conversa

Detalhar quais dados do paciente serao obrigatorios e como o agendamento diario deve funcionar na pratica.

## 2026-03-21 - Continuacao

### Diretriz de uso

- O sistema precisa ser simples, porque a equipe da clinica nao tem muita familiaridade com tecnologia.
- A prioridade e adiantar o servico deles com um fluxo direto e facil de usar.

### Novo foco da conversa

Primeiro vamos definir os dados do paciente.

### Dados do paciente definidos

Campos do paciente:

- nome completo
- data de nascimento
- telefone
- sexo
- cpf
- observacao
- email

Campos obrigatorios:

- nome completo
- telefone

### Regra do atendimento diario

- O atendimento sera por ordem de chegada.
- A data e o horario podem ser obtidos automaticamente a partir da criacao do registro no banco.

### Duvida em aberto

Definir quais status a consulta deve ter no fluxo diario.

### Novo foco da conversa

Definir os campos exatos do objeto Consulta.

### Ajuste de decisao

- O campo status foi removido do objeto Consulta para manter o fluxo mais simples.

### Proximo ponto

Definir os campos do objeto Medico.

### Ajuste no Medico

- Adicionar o campo CRM ao cadastro do medico.

### Tipo de consulta definido

- O tipo da consulta tera apenas duas opcoes:
- primeira consulta
- retorno

### Diretriz tecnica

- O sistema precisa continuar simples, inclusive na divisao dos apps do Django.

### Novo foco da conversa

Definir como dividir os apps do Django.

### Estrutura tecnica inicial

- Havera um app de autenticacao para permitir customizacao do model `User`.
- Em vez de `core`, a base compartilhada do projeto ficara em `_seed`.
- Dentro de `_seed/models`, sera criado um `BaseModelDjango`.
- `BaseModelDjango` tera os campos `created_at` e `updated_at`.
- Dentro de `_seed/models`, tambem sera criado um model de `SoftDelete`.
- `SoftDeleteModel` tera os campos `deleted` com default `False` e `deleted_at`.
- A regra de soft delete existe para que recepcionistas nao excluam consultas de forma definitiva, apenas tenham a sensacao de exclusao.

### Ajuste no app de autenticacao

- O app `authentication` tambem tera uma pasta `models`.
- O acesso ao admin devera ocorrer com `email` em vez de `username`.

### Ajuste no soft delete

- O soft delete passara a usar `is_deleted` e `deleted_at`.
- O model tera `objects` filtrando registros ativos por padrao.
- O model tera `all_objects` para acesso completo aos registros.
- O model tera suporte a `hard_delete()` e `restore()`.

### App de clinica

- O app `clinic` foi criado.
- O app `clinic` ja possui a pasta `models`.
- Os models concretos ainda nao serao criados agora.
- Antes disso, os campos de cada model serao definidos com mais cuidado.

### Ajustes na modelagem

- As docstrings devem ser escritas em portugues.
- Deve existir um model separado para email.
- Deve existir um model separado para telefone.
- Um paciente podera ter mais de um telefone e mais de um email.
- Um medico podera ter mais de um telefone e mais de um email.
- A forma de pagamento tera as opcoes:
- Dinheiro
- Pix
- Cartao de Credito
- Cartao de Debito

### Padronizacao de nomes

- Os nomes das classes devem ser em ingles.
- O model do paciente sera `Client`.
- O model do medico sera `Doctor`.

### Ajuste de modelagem para contatos

- Foi escolhida a abordagem com `ManyToMany` para telefones e emails.

### Esqueleto inicial dos models da clinica

- Foram criados os models `Client`, `Doctor`, `Appointment`, `Phone` e `Email`.
- `Client` e `Doctor` usam `ManyToMany` para `Phone` e `Email`.
- As docstrings dos models foram escritas em portugues.
- Os campos receberam descricao com `verbose_name` e `help_text`.

## 2026-03-24

### Novo foco da conversa

Organizar o Django Admin de forma modular e preparar a aplicacao para execucao em container.

### Estruturacao do admin

- Cada app passara a ter uma pasta `admin`.
- Dentro de cada pasta `admin`, deve existir um arquivo separado para cada model do app.
- A organizacao foi aplicada no app `authentication`.
- A organizacao foi aplicada no app `clinic`.

### Admin do app authentication

- Foi criado um arquivo especifico para o model `User`.
- O admin do usuario continua baseado em `UserAdmin`.
- O login administrativo segue usando `email`.

### Admin do app clinic

- Foi criado um arquivo de admin para `Client`.
- Foi criado um arquivo de admin para `Doctor`.
- Foi criado um arquivo de admin para `Appointment`.
- Foi criado um arquivo de admin para `Phone`.
- Foi criado um arquivo de admin para `Email`.
- Foram definidos `list_display`, `search_fields`, `list_filter` e `filter_horizontal` conforme o tipo de model.

### Ajuste estrutural importante

- Os arquivos antigos `admin.py` dos apps foram removidos.
- Foi mantido apenas o pacote `admin/` em cada app.
- Essa decisao evita ambiguidade de importacao entre modulo e pacote com o mesmo nome.
- A validacao com `manage.py check` passou sem erros.

### Containerizacao inicial

- Foi criado um `Dockerfile` na raiz do projeto.
- O `Dockerfile` usa build em duas etapas.
- A primeira etapa instala dependencias com Poetry.
- A etapa final copia apenas o necessario para executar a aplicacao.
- A imagem final roda com usuario nao root.
- O script de inicializacao fica em `infra/scripts/run-backend.sh`.

### Regras definidas para o script de inicializacao

- A espera por conexao com o banco ficou opcional e depende de `DB_HOST` e `DB_PORT`.
- Redis nao sera usado.
- RabbitMQ nao sera usado.
- O script pode aplicar migrations quando `RUN_MIGRATIONS=true`.
- O script pode garantir a criacao de um superusuario quando `CREATE_SUPERUSER=true`.
- A criacao do superusuario foi adaptada para o model de usuario autenticado por `email`.
- A aplicacao inicia com `runserver` na porta definida por `APP_RUN_PORT`, com fallback para `8000`.

### Validacao realizada

- O script `run-backend.sh` foi validado com `bash -n`.
- A imagem Docker ainda nao foi testada com `docker build`.

### Proximo ponto natural da conversa

Definir se o proximo passo sera criar `docker-compose.yml`, configurar Postgres ou continuar evoluindo o admin do Django.
