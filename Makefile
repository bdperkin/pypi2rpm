.DEFAULT_GOAL := help

.PHONY: help

PYTHON_VERSION ?= 3
PYTHON_BIN ?= python$(PYTHON_VERSION)

help: ## Display help information
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clean environment
	@echo "Cleaning environment"
	$(RM) -r *~

clean-all: clean ## Clean environment including the virtual env and cache
	@echo "Cleaning everything. You will need to recreate your venv!"
	$(RM) -r .cache/ pypi2rpm/version.py venv/

venv: clean ## Create isolated Python environment
	@echo "Creating isolated $(PYTHON_BIN) environment"
	$(eval PYTHON_MINOR_VERSION := $(shell $(PYTHON_BIN) --version | cut -d . -f 2))
	if [ $(PYTHON_MINOR_VERSION) -lt 10 ]; then \
		echo "Minimum Python version to use pypi2rpm is 3.10" && exit 1; \
	fi
	$(PYTHON_BIN) -m venv venv;
	venv/bin/pip install -U pip
	venv/bin/pip install -e .
