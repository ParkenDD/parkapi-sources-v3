
.PHONY: test
test:
	python -m pytest tests --cov=src --cov-report=html:reports/coverage_html/

.PHONY: open-coverage
open-coverage:
	@test -f ./reports/coverage_html/index.html || make test
	$(or $(BROWSER),firefox) ./reports/coverage_html/index.html


.PHONY: lint
lint: ruff-format ruff


.PHONY: ruff-format
ruff-format:
	ruff format ./src ./tests


.PHONY: ruff
ruff:
	ruff check --fix ./src ./tests
