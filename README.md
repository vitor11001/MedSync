# MedSync

O **MedSync** é um sistema de gestão para clínicas médicas voltado à organização da rotina operacional, ao controle financeiro das consultas e à emissão de relatórios gerenciais. O projeto foi desenvolvido para centralizar processos essenciais do dia a dia da clínica em uma única aplicação, reduzindo retrabalho, melhorando a rastreabilidade das informações e trazendo mais clareza para a operação.

Na prática, o sistema já entrega uma base sólida para uso administrativo: cadastro de pacientes, médicos e especialidades, registro de consultas, lançamento de pagamentos, configuração de regras de repasse e geração de relatórios em PDF. Hoje, o foco principal do produto está no **backoffice da clínica**, com interface construída sobre o Django Admin.

## Sumário

- [Visão geral](#visão-geral)
- [Principais funcionalidades](#principais-funcionalidades)
- [Escopo atual do projeto](#escopo-atual-do-projeto)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Estrutura do sistema](#estrutura-do-sistema)
- [Rotas principais](#rotas-principais)
- [Instalação e execução com Docker](#instalação-e-execução-com-docker)
- [Execução local sem Docker](#execução-local-sem-docker)
- [Comandos do projeto](#comandos-do-projeto)
- [Relatório de consultas](#relatório-de-consultas)
- [Backups do banco](#backups-do-banco)
- [Roadmap sugerido](#roadmap-sugerido)
- [Estado atual do repositório](#estado-atual-do-repositório)

## Visão geral

O MedSync foi pensado para apoiar a administração de clínicas que precisam acompanhar consultas e recebimentos com mais controle. Em vez de concentrar a operação em planilhas soltas ou rotinas manuais, o sistema organiza as informações em um fluxo único, com cadastros estruturados e regras financeiras ligadas a cada atendimento.

Atualmente, o sistema permite:

- Organizar o cadastro operacional da clínica.
- Registrar consultas com código único.
- Lançar um ou mais pagamentos por consulta.
- Calcular automaticamente o repasse do médico e a parcela da clínica.
- Emitir relatórios por médico ou consolidados em PDF.

## Principais funcionalidades

### Cadastros administrativos

- Cadastro de pacientes com validações de CPF, data de nascimento e contatos.
- Cadastro de médicos com CRM, contatos e vínculo com especialidades.
- Cadastro de especialidades médicas.
- Cadastro de formas de pagamento com ordenação e controle de ativação.

### Operação de consultas

- Registro de consultas com código identificador único.
- Associação da consulta ao paciente, médico e usuário criador.
- Campo de observações para uso operacional.
- Controle de edição após a criação, preservando a integridade do lançamento.

### Controle financeiro

- Registro de múltiplos pagamentos para a mesma consulta.
- Regras de repasse por médico e forma de pagamento.
- Cálculo automático do valor do médico e do valor da clínica em cada pagamento.
- Resumo financeiro da consulta diretamente no admin.

### Relatórios

- Emissão de relatório de consultas em PDF.
- Filtro por médico específico ou por todos os médicos.
- Consolidação por período.
- Total por forma de pagamento.
- Total geral do médico e da clínica.
- Numeração consistente por consulta, mesmo quando há múltiplos pagamentos.

### Acesso e autenticação

- Autenticação com modelo de usuário customizado baseado em e-mail.
- Painel administrativo disponível em `/admin/`.
- Endpoint autenticado para emissão de relatório em `/api/clinic/reports/appointments/`.

## Escopo atual do projeto

O projeto já atende bem o fluxo **administrativo, operacional e financeiro** da clínica, especialmente no contexto de cadastro, consultas, pagamentos e relatórios.

Por outro lado, é importante registrar com clareza que o MedSync, no estado atual, **ainda não é um prontuário eletrônico completo**. O sistema está mais maduro como plataforma de backoffice clínico-financeiro do que como solução clínica assistencial completa.

## Tecnologias utilizadas

- Python 3.12
- Django 6
- Django REST Framework
- ReportLab para geração de PDFs
- PostgreSQL no ambiente Docker
- SQLite como fallback local
- Docker Compose
- Nginx

## Estrutura do sistema

Principais apps do projeto:

- `authentication`: autenticação e gerenciamento de usuários.
- `clinic`: pacientes, médicos, especialidades, consultas e relatórios.
- `payments`: formas de pagamento, pagamentos de consultas e regras de repasse.

## Rotas principais

- `/`: redireciona para o admin.
- `/admin/`: painel administrativo principal.
- `/api/clinic/reports/appointments/`: endpoint autenticado para emissão de relatório de consultas em PDF.

## Instalação e execução com Docker

Esta é a forma recomendada para rodar o projeto localmente.

### Requisitos

- Docker
- Docker Compose
- `make`, opcionalmente, para usar os atalhos do `Makefile`

### Subindo o ambiente

Antes de subir o ambiente pela primeira vez, crie seu arquivo `.env` local:

```bash
cp .env.example .env
```

```bash
make build
make up
```

Sem `make`:

```bash
docker compose build
docker compose up -d
```

### O que acontece na inicialização

Ao subir o container `web`, o script de inicialização:

- aguarda o PostgreSQL ficar disponível;
- gera migrations com `makemigrations`;
- aplica migrations com `migrate`;
- garante a existência de um superusuário padrão;
- inicia o servidor Django.

### Acessos

- Aplicação: `http://localhost/`
- Admin: `http://localhost/admin/`

### Credenciais padrão do superusuário

Definidas no `.env`:

- E-mail: `admin@example.com`
- Senha: `Admin@12345`

### Encerrando o ambiente

```bash
make down
```

Para derrubar tudo removendo também os volumes:

```bash
make destroy
```

### Serviço de backup automático

Ao subir o ambiente com Docker, o serviço `dbbackup` também é iniciado. Ele executa backups automáticos do PostgreSQL em intervalo fixo.

Configuração atual no `docker-compose.yml`:

- intervalo entre backups: `86400` segundos, ou seja, 24 horas;
- retenção dos backups diários: `14` dias;
- retenção dos backups semanais: `35` dias;
- dia do backup semanal: `7`, ou seja, domingo;
- diretórios de saída no host: `backups/postgres/daily/` e `backups/postgres/weekly/`.

Os arquivos são salvos no seu repositório, fora do container, com nomes no formato:

```text
backups/postgres/daily/medsync_medsync_daily_YYYYMMDD_HHMMSS.sql.gz
backups/postgres/weekly/medsync_medsync_weekly_YYYYMMDD_HHMMSS.sql.gz
```

Exemplo:

```text
backups/postgres/daily/medsync_medsync_daily_20260402_231500.sql.gz
backups/postgres/weekly/medsync_medsync_weekly_20260406_000000.sql.gz
```

## Execução local sem Docker

Esse modo é útil para desenvolvimento rápido, testes e depuração local.

### Requisitos

- Python 3.12
- Ambiente virtual ativo
- Dependências instaladas

### Criando o ambiente virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Instalando as dependências

```bash
pip install poetry
poetry install --no-root
```

### Executando localmente

Sem variáveis de banco configuradas, o projeto utiliza SQLite automaticamente.

```bash
source .venv/bin/activate
python src/manage.py migrate
python src/manage.py runserver
```

Endereços locais:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin/`

### Usando PostgreSQL fora do Docker

Se quiser rodar o projeto com PostgreSQL local, configure as variáveis abaixo em um arquivo `.env` ou no ambiente:

```env
DB_NAME=medsync
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=Admin@12345
DJANGO_SUPERUSER_FIRST_NAME=Admin
DJANGO_SUPERUSER_LAST_NAME=User
```

Observação importante:

- o Django local lê o `.env` diretamente;
- o `docker compose` também usa o `.env`, mas o container `web` força `DB_HOST=dblocal` internamente para continuar funcionando com o PostgreSQL do Compose;
- isso permite manter um único `.env` no projeto sem deixar segredos reais hardcoded no `docker-compose.yml`.

## Comandos do projeto

### Comandos do Makefile

```bash
make build
make up
make down
make destroy
make migrations
make fpop
make backup
make restore FILE=backups/postgres/daily/arquivo.sql.gz
```

Descrição:

- `make build`: constrói as imagens Docker.
- `make up`: sobe os containers em background.
- `make down`: derruba os containers.
- `make destroy`: derruba os containers e remove volumes.
- `make migrations`: executa `makemigrations` e `migrate` no container `web`.
- `make fpop`: executa o seed de dados de demonstração.
- `make backup`: executa um backup manual imediato do banco usando o serviço `dbbackup`.
- `make restore FILE=...`: restaura um backup compactado `.sql.gz` no banco PostgreSQL do ambiente Docker.

### Comandos Django customizados

Com Docker:

```bash
docker compose exec web python3 /app/src/manage.py ensure_default_superuser
docker compose exec web python3 /app/src/manage.py ensure_default_specialties
docker compose exec web python3 /app/src/manage.py ensure_default_doctors
docker compose exec web python3 /app/src/manage.py ensure_default_payment_methods
docker compose exec web python3 /app/src/manage.py seed_demo_data
```

Com ambiente virtual local:

```bash
source .venv/bin/activate
python src/manage.py ensure_default_superuser
python src/manage.py ensure_default_specialties
python src/manage.py ensure_default_doctors
python src/manage.py ensure_default_payment_methods
python src/manage.py seed_demo_data
```

O que cada comando faz:

- `ensure_default_superuser`: cria o superusuário padrão quando ainda não existe nenhum.
- `ensure_default_specialties`: cria as especialidades padrão do sistema.
- `ensure_default_doctors`: cria o médico padrão usado no projeto.
- `ensure_default_payment_methods`: cria ou atualiza as formas de pagamento padrão.
- `seed_demo_data`: popula o banco com dados de demonstração para testes operacionais.

### Argumentos do seed

```bash
python src/manage.py seed_demo_data --patients 30 --appointments 120 --days 45 --seed 42
```

- `--patients`: quantidade de pacientes a gerar.
- `--appointments`: quantidade de consultas a gerar.
- `--days`: quantidade de dias cobertos na massa de dados.
- `--seed`: semente aleatória para reproduzir os mesmos dados.

### Comandos Django usuais

Localmente:

```bash
source .venv/bin/activate
python src/manage.py makemigrations
python src/manage.py migrate
python src/manage.py createsuperuser
python src/manage.py test
python src/manage.py runserver
```

No Docker:

```bash
docker compose exec web python3 /app/src/manage.py makemigrations
docker compose exec web python3 /app/src/manage.py migrate
docker compose exec web python3 /app/src/manage.py createsuperuser
docker compose exec web python3 /app/src/manage.py test
docker compose exec web python3 /app/src/manage.py runserver 0.0.0.0:8000
```

## Relatório de consultas

O sistema gera relatório em PDF com:

- filtro por médico específico ou por todos os médicos;
- período inicial e final;
- detalhamento por pagamento;
- total por forma de pagamento;
- total do médico;
- total da clínica;
- total geral do período.

Quando uma mesma consulta possui múltiplos pagamentos, ela pode aparecer em mais de uma linha no relatório. Nesses casos, o número da consulta é mantido igual entre as linhas correspondentes, facilitando a leitura humana do documento.

### Exemplo de chamada da API

O endpoint exige autenticação.

```bash
curl -X POST http://127.0.0.1:8000/api/clinic/reports/appointments/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "report_scope": "doctor",
    "doctor_id": 1,
    "start_date": "01/04/2026",
    "end_date": "30/04/2026"
  }'
```

Campos esperados:

- `report_scope`: `doctor` ou `all_doctors`
- `doctor_id`: obrigatório quando `report_scope` for `doctor`
- `start_date`: aceita `dd/mm/aaaa` ou `aaaa-mm-dd`
- `end_date`: aceita `dd/mm/aaaa` ou `aaaa-mm-dd`

## Backups do banco

O projeto agora possui backup automático do PostgreSQL no ambiente Docker.

### Como funciona

- O serviço `dbbackup` roda em paralelo com os demais containers.
- Ele aguarda o banco ficar disponível.
- Gera backups diários automaticamente.
- Gera backups semanais automaticamente no dia configurado.
- Cria dumps compactados com `pg_dump` em formato SQL compactado com `gzip`.
- Remove backups mais antigos que o período de retenção configurado para cada categoria.

Configuração padrão atual:

- backups diários com retenção de `14` dias;
- backups semanais com retenção de `35` dias;
- backup semanal executado no dia `7`, ou seja, domingo.

### Onde os backups ficam salvos

No host, os arquivos ficam em:

```text
backups/postgres/daily/
backups/postgres/weekly/
```

Esse diretório está montado no container, então os arquivos permanecem disponíveis mesmo após reinicializações dos serviços.

### Como gerar um backup manual

```bash
make backup
```

Ou diretamente:

```bash
docker compose exec dbbackup /bin/sh /app/infra/scripts/backup-db.sh once
```

Para gerar somente um backup diário:

```bash
docker compose exec dbbackup /bin/sh /app/infra/scripts/backup-db.sh daily
```

Para gerar somente um backup semanal:

```bash
docker compose exec dbbackup /bin/sh /app/infra/scripts/backup-db.sh weekly
```

### Como ajustar periodicidade e retenção

No serviço `dbbackup`, em `docker-compose.yml`, você pode alterar:

- `BACKUP_INTERVAL_SECONDS`: intervalo entre backups automáticos
- `BACKUP_DAILY_RETENTION_DAYS`: quantidade de dias mantidos para backups diários
- `BACKUP_WEEKLY_RETENTION_DAYS`: quantidade de dias mantidos para backups semanais
- `BACKUP_WEEKLY_DAY`: dia da semana em que o backup semanal será gerado, usando `1` a `7`

Exemplo:

```yaml
BACKUP_INTERVAL_SECONDS: 43200
BACKUP_DAILY_RETENTION_DAYS: 14
BACKUP_WEEKLY_RETENTION_DAYS: 35
BACKUP_WEEKLY_DAY: 7
```

Isso faria:

- um backup a cada 12 horas;
- retenção de 14 dias para os diários;
- retenção de 35 dias para os semanais;
- backup semanal aos domingos.

### Como restaurar um backup

Exemplo de restauração a partir de um arquivo salvo:

```bash
make restore FILE=backups/postgres/daily/medsync_medsync_daily_YYYYMMDD_HHMMSS.sql.gz
```

Também é possível restaurar um backup semanal:

```bash
make restore FILE=backups/postgres/weekly/medsync_medsync_weekly_YYYYMMDD_HHMMSS.sql.gz
```

Antes de restaurar em um ambiente já em uso, revise com cuidado o impacto, porque o dump é gerado com `--clean` e `--if-exists`, ou seja, ele recria os objetos do banco durante a restauração.

## Roadmap sugerido

Próximas evoluções naturais para o projeto:

- área de prontuário clínico e histórico assistencial;
- agenda operacional com visão por dia e por profissional;
- dashboard financeiro com indicadores e filtros;
- exportações em formatos adicionais, como CSV e Excel;
- trilha de auditoria mais detalhada para ações críticas;
- perfis de acesso com permissões mais granulares;
- APIs adicionais para integração com sistemas externos.

## Estado atual do repositório

- Versão atual: `0.1.0`
- Interface principal: Django Admin
- Foco funcional atual: operação administrativa, financeira e emissão de relatórios
