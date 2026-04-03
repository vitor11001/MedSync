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

## 2026-04-02

### Novo foco da conversa

Evoluir o sistema em cima do fluxo administrativo atual, corrigindo falhas do admin, refinando o relatório, melhorando a documentação do projeto e preparando a infraestrutura local com favicon, backups e variáveis de ambiente.

### Ajustes no admin de consultas

- Foi corrigido um erro na tela de edição de consultas no Django Admin causado por concatenação incorreta entre `list` e `tuple` em `get_readonly_fields`.
- Foi corrigido um segundo problema no inline de pagamentos, que quebrava a renderização da tela de edição ao montar o `empty_form`.
- Foi adicionado teste de regressão para garantir que a tela de alteração da consulta continue abrindo normalmente.

### Ajuste no relatório de consultas

- O número exibido no relatório passou a ser por consulta, e não mais por item de pagamento.
- Quando a mesma consulta aparece em várias linhas por causa de múltiplos pagamentos, todas as linhas agora compartilham o mesmo número.
- Esse comportamento foi coberto por teste.

### Reescrita do README

- O `README.md` foi refeito com linguagem mais adequada para leitura humana.
- O documento passou a descrever o projeto como sistema de backoffice clínico-financeiro.
- Foram documentadas as funcionalidades atuais, a stack, os modos de execução, os comandos disponíveis, o relatório em PDF e o estado atual do produto.
- O README também passou a documentar o uso de `.env`, backups automáticos e restauração do banco.

### Favicon do projeto

- O favicon passou a ser servido apenas pelo Nginx no ambiente Docker.
- A URL `/favicon.ico` passou a redirecionar para `/favicon-32x32.png`.
- O admin foi configurado para apontar diretamente para o favicon servido pelo Nginx.
- O fallback de favicon pelo Django foi removido.

### Regras para formas de pagamento

- O campo de ordem de exibição foi removido.
- A ordenação passou a ser alfabética pelo campo `name`.
- O nome da forma de pagamento passou a ser normalizado ao salvar:
- remoção de espaços nas extremidades;
- conversão para minúsculas.
- O nome passou a ter limite de 50 caracteres.
- Não podem existir duas formas de pagamento com o mesmo nome após a normalização.
- O nome da forma de pagamento passou a ser imutável após a criação.
- Após criar uma forma de pagamento, no admin apenas o campo `is_active` pode ser alterado.
- A exibição no admin passou a usar capitalização amigável por palavra, como `Pix - Casa Forte`, mesmo com o valor persistido em minúsculas no banco.
- Foi criada migração para remover `sort_order`, ajustar o tamanho do campo e normalizar registros antigos.
- Foram adicionados e ajustados testes para cobrir normalização, unicidade, ordenação, imutabilidade e exibição.

### Backups automáticos do banco

- Foi criado um serviço `dbbackup` no `docker-compose.yml`.
- O ambiente Docker passou a gerar backups automáticos do PostgreSQL.
- Foram configurados backups diários com retenção de 14 dias.
- Foram configurados backups semanais com retenção de 35 dias.
- Os backups semanais ficaram definidos para o dia 7 da semana, ou seja, domingo.
- Os arquivos passaram a ser salvos no host em:
- `backups/postgres/daily/`
- `backups/postgres/weekly/`
- Foi criado o comando `make backup` para backup manual imediato.
- Foi criado o comando `make restore FILE=...` para restaurar um arquivo `.sql.gz`.
- O README foi atualizado com instruções de backup e restauração.

### Variáveis de ambiente do projeto

- O `docker-compose.yml` deixou de carregar valores sensíveis fixos diretamente no arquivo.
- O projeto passou a usar `.env` e `.env.example`.
- Foi criado um `.env.example` com valores padrão de aplicação, banco, superusuário e backups.
- Foi criado um `.env` inicial no formato padrão para posterior edição manual.
- O fluxo com `docker compose` foi preservado.
- O container `web` continua forçando `DB_HOST=dblocal` internamente para manter a integração com o PostgreSQL do Compose.

### Situação final desta rodada

- O projeto saiu desta conversa com admin mais estável, relatório mais legível, documentação mais forte e infraestrutura local mais preparada para uso real.
- Foram validados testes automatizados relevantes ao longo da rodada após as alterações principais.

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

## 2026-03-29 - Pagamento multiplo por consulta

### Novo ajuste de regra de negocio

- Foi identificado que uma consulta nao pode mais assumir apenas uma unica forma de pagamento.
- Na pratica, muitos pacientes pagam a mesma consulta usando mais de uma forma de pagamento.

### Decisao de modelagem

- Foi decidido que a forma correta de evoluir o sistema sera criar um model proprio de pagamento vinculado a consulta.
- A abordagem escolhida foi separar os pagamentos em um model dedicado, em vez de manter apenas um unico campo `payment_method` na consulta.
- Essa estrutura permitira registrar uma ou varias formas de pagamento na mesma consulta.

### Impacto esperado

- O repasse financeiro deixara de depender de um unico campo `payment_method` na consulta.
- O calculo de repasse devera passar a considerar cada pagamento individualmente.
- O total consolidado da consulta continuara existindo, mas os pagamentos serao registrados separadamente.

### Proximo passo definido

- O proximo passo da implementacao sera criar um model proprio para pagamentos da consulta.
- Esse novo model devera permitir multiplos pagamentos por consulta e preparar a base para recalcular repasses por forma de pagamento.

## 2026-03-29 - Continuacao - Implementacao do pagamento multiplo

### Regra de negocio confirmada

- Foi confirmado que uma consulta pode receber mais de uma forma de pagamento.
- Exemplo aceito no fluxo:
- uma consulta de `300` pode ser paga com `200` em dinheiro e `100` no cartao de credito.

### Decisao final de modelagem

- Foi descartada a abordagem com relacao `OneToOne` entre consulta e pagamento.
- Foi escolhida a relacao `1:N` entre `Appointment` e pagamentos.
- A consulta continua sendo o registro principal do atendimento.
- Cada item de pagamento passou a ser registrado separadamente.

### Estrutura definida

- `Appointment` passou a representar apenas a consulta.
- `Appointment` passou a manter o campo `total_amount` como valor total da consulta.
- Foi criado o model `AppointmentPayment`.
- Cada `AppointmentPayment` possui:
- consulta
- forma de pagamento
- valor
- percentual do medico
- percentual da clinica
- valor do medico
- valor da clinica
- criado por
- recebido em

### Regra de repasse

- O repasse financeiro deixou de ser calculado no nivel da consulta inteira.
- O repasse agora e calculado item a item, por pagamento.
- Cada pagamento congela seu proprio snapshot financeiro no momento da criacao.
- As regras de `DoctorPaymentSplitRule` continuam existindo.
- As regras passaram a ser aplicadas por forma de pagamento em cada item de `AppointmentPayment`.

### Decisao de interface no admin

- Foi decidido manter a tela da consulta como ponto principal de uso da recepcao.
- Os pagamentos passaram a aparecer dentro da propria consulta como inline.
- A abordagem escolhida foi `TabularInline`.
- O objetivo e permitir registrar a consulta e seus pagamentos na mesma tela, sem abrir um fluxo separado.

### Validacoes definidas para o admin

- Toda consulta deve ter pelo menos um pagamento.
- A soma dos pagamentos deve ser exatamente igual ao `total_amount` da consulta.
- Nao sera permitido pagamento com valor zero ou negativo.
- Nesta primeira versao, a consulta deve sair totalmente quitada.
- Nao foi aberto suporte para saldo pendente, troco, estorno ou parcelamento.

### Comportamento apos criacao

- A consulta continua seguindo a ideia de congelamento operacional apos ser criada.
- Depois da criacao, apenas a observacao da consulta continua editavel pelo usuario criador.
- Os pagamentos ficam visiveis para auditoria, mas nao foram deixados livres para edicao posterior.

### Relatorios

- O relatorio de consultas deixou de depender de um unico `payment_method` na consulta.
- Os totais do relatorio passaram a ser calculados a partir dos itens de `AppointmentPayment`.
- O total por forma de pagamento passou a consolidar os itens registrados em cada consulta.
- Os totais do medico e da clinica passaram a somar os snapshots congelados de cada pagamento.

### Seed e dados de teste

- O seed de dados falsos foi adaptado para o novo fluxo.
- O seed agora cria consultas com um ou mais pagamentos.
- O seed continua criando regras de repasse por medico e forma de pagamento.

### Banco de dados e migrations

- Como o banco ainda esta em fase de testes, foi aceita a estrategia de rebaseline do schema.
- Foi decidido nao migrar dados antigos.
- As migrations antigas do app `clinic` foram substituidas por uma nova migration inicial refletindo a modelagem nova.
- Essa decisao tambem resolveu o problema anterior de migrations quebradas no app `clinic`.

### Validacao tecnica realizada

- `manage.py check` passou sem erros.
- A suite de testes passou apos a refatoracao.
- Foram adicionados testes cobrindo:
- snapshot de repasse por item de pagamento
- validacao da soma dos pagamentos no inline
- consolidacao correta do relatorio com pagamento multiplo

### Observacao importante para retomada

- O codigo ja ficou ajustado para pagamento multiplo por consulta.
- Para subir o ambiente novamente com consistencia, o banco de testes pode ser recriado do zero.
- O proximo passo natural, se necessario, e evoluir o fluxo para suportar saldo pendente, edicao controlada de pagamentos ou regras mais avancadas de recebimento.
