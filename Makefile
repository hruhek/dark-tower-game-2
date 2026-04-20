.DEFAULT_GOAL := help

.PHONY: help test lint

## Show this help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^## / { printf "\n\033[1m%s\033[0m\n", substr($$0, 4) } ' $(MAKEFILE_LIST)

## Run all tests
test:
	uv run pytest -v

## Lint and type check
lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run ty check
