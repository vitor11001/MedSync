.PHONY: destroy down build up migrations fpop

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
