.PHONY: destroy down build up migrations fpop backup restore

destroy:
	docker compose down -v

down:
	docker compose down

build:
	docker compose build

up:
	docker compose up -d

migrations:
	docker compose exec web python3 /app/src/manage.py makemigrations
	docker compose exec web python3 /app/src/manage.py migrate

fpop:
	docker compose exec web python3 /app/src/manage.py seed_demo_data

backup:
	docker compose exec dbbackup /bin/sh /app/infra/scripts/backup-db.sh once

restore:
	@test -n "$(FILE)" || (echo "Uso: make restore FILE=backups/postgres/daily/arquivo.sql.gz" && exit 1)
	gzip -dc "$(FILE)" | docker compose exec -T dblocal psql -U postgres -d medsync
