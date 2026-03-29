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

## 2026-03-28

### Novo foco da conversa

Revisar o estado real do projeto, corrigir a base tecnica e iniciar a personalizacao do Django Admin como interface principal do sistema.

### Diagnostico realizado

- Foi constatado que o projeto tinha models e admin iniciais, mas ainda nao tinha migrations versionadas.
- Foi constatado que o `migrate` no container falhava porque os apps locais `authentication` e `clinic` nao tinham migrations commitadas.
- Foi constatado que os testes existentes estavam praticamente ausentes.

### Ajustes tecnicos iniciais

- Foram geradas as migrations iniciais dos apps `authentication` e `clinic`.
- O script `run-backend.sh` passou a aceitar `RUN_MAKEMIGRATIONS=true` antes do `RUN_MIGRATIONS=true`.
- Foi mantido que o fluxo recomendado continua sendo versionar migrations no repositorio, e nao depender de `makemigrations` automatico por padrao.

### Superusuario padrao

- Foi decidido que o sistema deve conseguir criar automaticamente uma conta administrativa padrao.
- A criacao do admin passou a ocorrer por um comando proprio de gerenciamento: `ensure_default_superuser`.
- O comando cria o superusuario apenas se ainda nao existir nenhum superusuario no banco.
- As configuracoes do superusuario padrao passaram a usar `pydantic-settings`, em vez de `os.getenv` direto.
- O `docker-compose.yml` ficou configurado para subir com `CREATE_SUPERUSER=true`.
- A senha padrao definida para bootstrap local ficou mais forte que a inicial.

### Ajustes de navegacao e identidade do admin

- A rota raiz `/` passou a redirecionar para `/admin/`.
- O nome exibido no admin foi definido como `Portal MedSync`.
- O idioma global do Django foi configurado como `pt-br`.
- O fuso horario global do Django foi configurado como `America/Recife`.

### Organizacao visual do admin

- O app `authentication` passou a aparecer no admin como `Usuarios e Acessos`.
- O app `clinic` passou a aparecer no admin como `Clinica`.
- O model de `Group` passou a aparecer junto da area de autenticacao por meio de um proxy model no app `authentication`.
- Os nomes exibidos dos models no admin passaram para portugues:
- `Usuario`
- `Grupo`
- `Paciente`
- `Medico`
- `Consulta`
- `Telefone`
- `Email`

### Ajustes de estaticos

- Foi adicionado `STATIC_ROOT` no settings para permitir `collectstatic`.
- Foi validado que o arquivo estatico customizado do admin e encontrado pelo Django.
- Foi validado que `python manage.py collectstatic --noinput` funciona corretamente.

### Ajustes no cadastro de paciente

- Foi decidido que o campo `sexo` do paciente deve ser definido no proprio model com duas opcoes:
- `Masculino`
- `Feminino`
- O admin de `Paciente` passou a usar um formulario customizado.
- No formulario de `Paciente`, os campos `is_deleted` e `deleted_at` nao devem aparecer na criacao nem na edicao.
- O campo `cpf` passou a aceitar apenas 11 numeros e deve ser salvo formatado como `xxx.xxx.xxx-xx`.
- Foi adicionada mascara visual para CPF no formulario do admin.
- O campo `data de nascimento` passou a ser digitado manualmente no formato `dd/mm/aaaa`.
- Foi adicionada mascara visual para `data de nascimento`.
- Foi definido que entradas incompletas como `01/03/98` devem ser rejeitadas com mensagem clara, exigindo ano completo.

### Decisao sobre telefones e emails

- Foi tentada uma mudanca estrutural para transformar `Phone` e `Email` em registros com dono direto.
- Depois da conversa, essa mudanca foi desfeita porque a regra real do negocio permite compartilhamento de telefone entre pessoas, como marido e mulher ou mae e filho.
- A migration `0003` que fazia essa alteracao estrutural foi removida.
- Os models voltaram a usar `ManyToMany` para telefones e emails.
- Mesmo mantendo a modelagem atual, foi decidido que `Telefone` e `Email` nao devem mais aparecer como itens independentes no menu do admin.

### Ponto em aberto

- Ainda falta definir a melhor UX para telefones e emails dentro do cadastro de `Paciente` e, depois, de `Medico`.
- Existe a restricao atual de tentar melhorar isso sem alterar os models.

### Proximo ponto natural da conversa

Definir como `telefone` e `email` devem aparecer e ser cadastrados no admin de `Paciente` sem expor esses models no menu lateral.

## 2026-03-29

### Novo foco da conversa

Evoluir o admin como interface principal do sistema, consolidar a modelagem atual da clinica e iniciar a emissao de relatorios em PDF.

### Ajuste de modelagem para contatos

- Foi abandonada a abordagem com models separados de `Phone` e `Email`.
- `Client` passou a ter os campos:
- `phone_primary`
- `phone_secondary`
- `email`
- `Doctor` passou a ter os campos:
- `phone_primary`
- `phone_secondary`
- `email`
- O cadastro de `Paciente` e `Medico` passou a validar telefone com exatamente 11 numeros.
- Foi adotada mascara visual de telefone no admin no formato `(81) 97106-6662`.
- O campo `email` recebeu `placeholder` no formulario do admin.

### Ajustes de apresentacao e validacao

- O campo `sexo` do paciente passou a ser obrigatorio.
- O campo `Data de nascimento` no admin foi corrigido para exibicao em portugues e com texto de ajuda.
- O campo `CRM` no formulario do medico passou a aparecer em letras maiusculas.
- Os nomes de `Paciente`, `Medico` e `Especialidade` passaram a ser salvos em minusculo.
- A exibicao desses nomes no admin e nas representacoes textuais passou a usar iniciais maiusculas.
- O `__str__` de `Client` passou para o formato:
- `Nome Completo | CPF: xxx.xxx.xxx-xx`
- O `__str__` de `Doctor` passou para o formato:
- `Nome Completo | CRM: xxxxxx`

### Especialidades dos medicos

- O campo `specialty` de `Doctor` foi substituido por `specialties` com `ManyToMany`.
- Foi criado o model `Specialty`.
- Foi criado o admin de `Especialidades`.
- O formulario de `Especialidade` no admin nao mostra `is_deleted` nem `deleted_at`.
- Foi criado o comando `ensure_default_specialties`.
- As especialidades padrao definidas foram:
- `Mastologista`
- `Clinico Geral`
- `Medico do Trabalho`
- Foi criado o comando `ensure_default_doctors`.
- O comando cria o medico inicial:
- `Aluizio João da Silva Filho`
- CRM `6654`
- especialidade `Mastologista`

### Ajustes no admin

- O admin de `Paciente` e `Medico` deixou de exibir filtros laterais.
- O admin de `Consulta` deixou de exibir `is_deleted` no formulario e na listagem principal.
- O admin de `Consulta` passou a usar `autocomplete` para `Paciente` e `Medico`.
- A busca de `Paciente` ficou limitada a:
- `full_name`
- `cpf`
- A busca de `Medico` ficou limitada a:
- `full_name`
- `crm`
- O admin de `Consulta` ganhou uma pagina propria para emissao de relatorio usando o layout do Django Admin.

### Sequencia e codigo da consulta

- Foi criado o campo `code` em `Appointment` como codigo operacional da consulta.
- O codigo usa o formato:
- `C-YYYYMMDD-XXXX`
- Foi criado o model auxiliar `AppointmentDailySequence`.
- A geracao do codigo passou a usar transacao atomica com `select_for_update()` para evitar colisao concorrente.
- O codigo da consulta passou a aparecer na listagem do admin e na busca.

### Tipos de consulta e pagamentos

- O tipo de consulta passou a iniciar no admin com `Primeira consulta`.
- As opcoes de `tipo de consulta` passaram a incluir:
- `Primeira consulta`
- `Retorno`
- `ASO`
- `Procedimento`
- A forma de pagamento passou a incluir:
- `Dinheiro`
- `Pix`
- `Cartao de Credito`
- `Cartao de Debito`
- `Plano de Saude`
- O campo `valor pago` passou a usar mascara monetaria no admin com centavos automaticos.

### Nginx e estaticos

- Foi configurado um servico `nginx` no `docker-compose`.
- O acesso ao sistema passou a ser feito por `http://localhost`.
- Os arquivos estaticos passaram a ser servidos pelo `nginx`.
- O arquivo JS customizado do admin foi movido da saida de `staticfiles` para a origem correta em `clinic/static`.

### Pagina e API de relatorio

- Foi criada uma pagina propria de relatorio no admin de `Consulta`.
- A pagina possui:
- selecao obrigatoria de um medico especifico ou `Todos os medicos`
- `Data inicial`
- `Data final`
- botao para emitir o PDF
- Foi criado `AppointmentReportForm` para validar medico e periodo.
- O periodo maximo permitido ficou definido em ate 3 meses.
- Foi criado um endpoint DRF:
- `POST /api/clinic/reports/appointments/`
- Foi criada uma pasta `views` no app `clinic`.
- Foi criada uma pasta `controllers` no app `clinic`.
- Foi criada uma pasta `serializers` no app `clinic`.

### Estrutura do relatorio em PDF

- Foi escolhida a biblioteca `ReportLab`.
- O PDF passou a ser gerado por um controller dedicado separado do controller de dados.
- O relatorio ganhou cabecalho com:
- nome da empresa
- nome do medico
- CRM
- periodo do relatorio
- O relatorio passou a aceitar tambem o caso de `Todos os medicos`, quebrando o documento por medico.
- A tabela do relatorio foi definida com as colunas:
- `Nº`
- `Codigo`
- `Paciente`
- `Tipo`
- `Pagamento`
- `Valor`
- `Observacao`
- A coluna `Nº` passou a ser sequencial dentro do conjunto filtrado, e nao o `id` da consulta.
- O `Codigo` da consulta passou a aparecer logo apos `Nº`.
- A coluna `Horário` foi removida depois dos testes visuais.
- A observacao passou a ser limitada aos 100 primeiros caracteres.
- O relatorio passou a exibir totais por forma de pagamento e total geral de faturamento.
- O PDF passou a abrir no navegador em vez de baixar automaticamente.
- O PDF passou a abrir em nova aba a partir da pagina do admin.
- O PDF ganhou paginacao no rodape no formato `pagina atual / total`.
- O layout do PDF foi refinado com:
- cabecalho institucional
- tabela principal estilizada
- box de totais
- quebra de pagina por medico

### Logo da clinica

- Foi definido um caminho fixo para o logo usado no PDF:
- `src/clinic_assets/logo-clinica.png`
- Foi criado um README no diretorio explicando esse caminho.
- O gerador do PDF passou a tentar incluir automaticamente o logo no cabecalho quando o arquivo existir.

### Ferramentas operacionais

- Foi criado um `Makefile` na raiz do projeto.
- Os atalhos definidos foram:
- `make destroy`
- `make down`
- `make build`
- `make up`
- `make migrations`
- `make fpop`
- Foi criado o comando `seed_demo_data` para popular o banco com dados falsos de teste.
- O comando cria especialidades, medicos, pacientes, consultas e um usuario de recepcao para testes.

### Logging

- Foi adicionada configuracao global de `LOGGING` no `settings.py`.
- A estrategia escolhida foi usar apenas o `root logger`.
- Foi decidido que o uso padrao no codigo sera com chamadas diretas como:
- `logging.info(...)`
- `logging.debug(...)`

### Observacao importante para retomada

- A pagina de relatorio do admin ja gera o PDF real.
- A API DRF de relatorio tambem ja gera o PDF real.
- O proximo passo natural, se necessario, e refinar layout, fontes, logo e regras de negocio do relatorio com base em testes reais de uso.

## 2026-03-30

### Novo foco da conversa

Consolidar o fluxo de relatorios em PDF, melhorar a apresentacao do documento e iniciar a modelagem financeira de repasse entre medico e clinica.

### Ajustes no relatorio em PDF

- O PDF passou a abrir diretamente no navegador, em vez de forcar download automatico.
- A abertura do PDF a partir da pagina do admin passou a ocorrer em nova aba.
- O titulo interno do PDF foi definido como `Relatorio de Consultas`.
- Foi adicionada paginacao no rodape do PDF no formato `pagina atual / total de paginas`.
- O rodape passou a exibir `Portal MedSync`.
- O layout do PDF foi refinado para ficar mais profissional, com:
- cabecalho institucional
- tabela principal com melhor alinhamento
- box de totais
- quebra de pagina por medico no relatorio consolidado
- Foi removida a coluna `Horário` da tabela principal do relatorio.
- A tabela principal passou a ter as colunas:
- `Nº`
- `Codigo`
- `Paciente`
- `Tipo`
- `Pagamento`
- `Valor`
- `Observacao`
- A tabela principal foi centralizada e recebeu mais respiro nas laterais.
- O logo da clinica foi ampliado no cabecalho do PDF.
- O cabecalho foi reorganizado para usar:
- logo a esquerda
- `MedSync` e `Relatorio de Consultas` centralizados na coluna da direita
- quadro com `Medico`, `CRM` e `Periodo` alinhado a direita

### Logo da clinica no PDF

- Foi decidido que o logo usado no PDF nao deve ficar em `staticfiles`.
- Foi definido um caminho proprio para o asset institucional:
- `src/clinic_assets/logo-clinica.png`
- Foi adicionada a configuracao `CLINIC_LOGO_PATH` no `settings.py`.
- O gerador do PDF passou a tentar carregar esse arquivo automaticamente quando ele existir.

### Logging

- Foi decidido usar configuracao global de `logging` no projeto, sem precisar registrar app por app.
- O `settings.py` passou a ter configuracao de `LOGGING` usando apenas o `root logger`.
- O formato escolhido para os logs foi:
- `data/hora | nivel | modulo | mensagem`
- Foi decidido que o padrao de uso no codigo sera:
- `logging.info(...)`
- `logging.debug(...)`
- sem usar `logger = logging.getLogger(__name__)`

### Regras de repasse financeiro

- Foi decidido modelar o repasse por medico e forma de pagamento.
- Foi criado o model `DoctorPaymentSplitRule`.
- Cada regra possui:
- medico
- forma de pagamento
- percentual do medico
- percentual da clinica
- ativo
- Foi definida a validacao de que os percentuais devem somar exatamente `100`.
- Foi criado o admin de `Regras de repasse`.

### Snapshot financeiro na consulta

- Foi decidido que a consulta deve guardar uma fotografia dos dados financeiros aplicados no momento da criacao.
- `Appointment` passou a armazenar:
- `doctor_percentage`
- `clinic_percentage`
- `doctor_amount`
- `clinic_amount`
- O calculo do repasse passou a acontecer na criacao da consulta.
- A consulta agora depende de existir uma regra ativa de repasse para o medico e a forma de pagamento.
- A logica de arredondamento foi definida assim:
- o eventual centavo residual deve favorecer a clinica
- o ajuste final fica no valor da clinica
- o medico recebe o restante
- Foi decidido que esses campos financeiros devem aparecer apenas como leitura na edicao da consulta.

### Ajustes no seed de dados falsos

- O comando `seed_demo_data` foi atualizado para refletir a modelagem financeira atual.
- O seed agora cria regras de repasse para os medicos de teste em todas as formas de pagamento.
- O seed continua criando especialidades, medicos, pacientes, consultas e usuario de recepcao.

### Data de nascimento do paciente

- Foi decidido que `data de nascimento` do paciente deve ser obrigatoria.
- O model `Client` passou a exigir `birth_date`.
- O formulario do admin de `Paciente` passou a exigir `Data de nascimento`.
- Foi criada migration especifica para esse ajuste.
- O seed de dados falsos passou a gerar data de nascimento para todos os pacientes criados.

### Observacao importante para retomada

- O relatorio em PDF ja esta funcional e com layout refinado.
- A base de repasse financeiro ja foi modelada, mas ainda pode exigir evolucao futura para relatórios financeiros detalhados.
- O proximo passo natural, se necessario, e levar os valores de repasse para relatorios financeiros especificos e telas operacionais da clinica.
