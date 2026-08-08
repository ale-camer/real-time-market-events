.PHONY: up down logs build

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f
