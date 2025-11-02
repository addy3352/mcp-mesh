SHELL := /bin/bash

.PHONY: build up down logs ps pull restart dbinit certs test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	systemctl restart mcp-mesh

logs:
	docker compose logs -f --tail=200

ps:
	docker compose ps

pull:
	git pull --rebase

dbinit:
	[ -f db/mesh.db ] || sqlite3 db/mesh.db < db/schema.sql

certs:
	certbot renew --dry-run && systemctl reload nginx

test:
	curl -fsS https://mesh.aditya-raman.com/api/mesh/garmin/latest | jq .
