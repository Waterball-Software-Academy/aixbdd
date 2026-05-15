# Python E2E starter commands.
#
# Common entry points:
#   make up              Run the FastAPI app with local PostgreSQL.
#   make behave-dry-run  Check Behave feature/step loading inside the Docker image.
#   make behave          Run acceptance tests inside the Docker image.
#
# `make up` reuses the existing compose app container when present. The test
# targets reuse IMAGE_NAME when it already exists. Use `make build` only when
# you intentionally want to rebuild the image.
#
# Behave uses Testcontainers, so Docker must be running on the host. The test
# targets mount the host Docker socket so the containerized test runner can start
# its PostgreSQL test container.

IMAGE_NAME ?= aixbdd-test-backend
APP_CONTAINER_NAME ?= aixbdd-test-backend-app
DOCKER_SOCKET ?= /var/run/docker.sock
TESTCONTAINERS_HOST_OVERRIDE ?= host.docker.internal

.PHONY: build ensure-image ensure-compose-runtime up down logs shell behave behave-dry-run test test-dry-run

build:
	docker build -t $(IMAGE_NAME) .

ensure-image:
	@if docker image inspect $(IMAGE_NAME) >/dev/null 2>&1; then \
		echo "Image $(IMAGE_NAME) already exists; skipping build."; \
	else \
		docker build -t $(IMAGE_NAME) .; \
	fi

ensure-compose-runtime:
	@if docker container inspect $(APP_CONTAINER_NAME) >/dev/null 2>&1; then \
		echo "Container $(APP_CONTAINER_NAME) already exists; skipping build."; \
	elif docker image inspect $(IMAGE_NAME) >/dev/null 2>&1; then \
		echo "Image $(IMAGE_NAME) already exists; skipping build."; \
	else \
		docker build -t $(IMAGE_NAME) .; \
	fi

up: ensure-compose-runtime
	docker compose up --no-build

down:
	docker compose down

logs:
	docker compose logs -f

shell: ensure-image
	docker run --rm -it \
		-v $(DOCKER_SOCKET):/var/run/docker.sock \
		--add-host=host.docker.internal:host-gateway \
		-e TESTCONTAINERS_HOST_OVERRIDE=$(TESTCONTAINERS_HOST_OVERRIDE) \
		$(IMAGE_NAME) \
		/bin/sh

behave: ensure-image
	docker run --rm \
		-v $(DOCKER_SOCKET):/var/run/docker.sock \
		--add-host=host.docker.internal:host-gateway \
		-e TESTCONTAINERS_HOST_OVERRIDE=$(TESTCONTAINERS_HOST_OVERRIDE) \
		$(IMAGE_NAME) \
		behave

behave-dry-run: ensure-image
	docker run --rm \
		-v $(DOCKER_SOCKET):/var/run/docker.sock \
		--add-host=host.docker.internal:host-gateway \
		-e TESTCONTAINERS_HOST_OVERRIDE=$(TESTCONTAINERS_HOST_OVERRIDE) \
		$(IMAGE_NAME) \
		behave --dry-run

test: behave

test-dry-run: behave-dry-run
