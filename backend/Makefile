# Configuration

COMPOSE = docker compose
BASE = -f compose.yml
CI = -f compose.ci.yml
DEV = -f compose.dev.yml
TEST = -f compose.test.yml

# Build targets

.PHONY: build build-dev build-test build-prod

build:
	$(COMPOSE) $(BASE) build

build-dev:
	$(COMPOSE) $(BASE) $(DEV) build

build-test:
	$(COMPOSE) $(CI) $(TEST) build

# Run targets

.PHONY: dev test prod

dev:
	$(COMPOSE) $(BASE) $(DEV) up

test:
	$(COMPOSE) $(CI) $(TEST) up --abort-on-container-exit

prod:
	$(COMPOSE) $(BASE) up

# Utility targets

.PHONY: down clean logs ps

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v --remove-orphans

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

