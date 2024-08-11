
.PHONY: install
install:
	poetry install

.PHONY: gen-docs
gen-docs: install
	poetry run python docs/appendixes/gen-appendix-links.py docs/

.PHONY: docs-live
docs-live: gen-docs
	docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material

.PHONY: docs-build
docs-build: gen-docs
	docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material build

.PHONY: build
build: install
	poetry build

.PHONY: test
test:
	poetry run pytest -s -x -rA

.PHONY: test-e2e
test-e2e:
	poetry run pytest --e2e -s -x -rA

.PHONY: test-e2e-model-registry
test-e2e-model-registry:
	poetry run pytest --e2e-model-registry -s -x -rA

.PHONY: lint
lint: install
	poetry run ruff check --fix

.PHONY: mypy
mypy: install
	poetry run mypy .
