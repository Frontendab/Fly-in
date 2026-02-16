# ? Makefile for Fly-in Project

VENV = venv

PYTHON = python3
PIP = ./$(VENV)/bin/pip
MYPY = ./$(VENV)/bin/mypy
FLAKE8 = ./$(VENV)/bin/flake8

PROGRAM_NAME = fly-in
CONFIG_FILE = config.txt

PACKAGES_TO_INSTALL = mypy flake8

PDB_COMMAND = $(PYTHON) -m pdb $(PROGRAM_NAME).py

CLEAN_COMMAND = rm -rf $$(find . -name "__pycache__" -o -name ".mypy_cache") $(VENV)

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			--disallow-untyped-defs --check-untyped-defs

LINT_COMMAND = $(FLAKE8) . --exclude $(VENV) & $(MYPY) . $(MYPY_FLAGS) --exclude $(VENV)

CREATE_VENV = $(PYTHON) -m venv $(VENV)

INSTALL_DEPS = $(PIP) install $(PACKAGES_TO_INSTALL)

# ? Install a Python package using pip
install:
	@echo "Installing dependencies..."
	@$(CREATE_VENV)
	@$(INSTALL_DEPS)
	@echo "Dependencies installed successfully."

# ? Run the program
run:
	@$(PYTHON) $(PROGRAM_NAME).py $(CONFIG_FILE)

# ? Debug the program
debug:
	@$(PDB_COMMAND)

# ? Clean the program
clean:
	@$(CLEAN_COMMAND)
	@echo "Program cleaned successfully."

# ? Lint the program
lint:
	$(LINT_COMMAND)

# ? Lint strict the program
lint-strict:
	@$(FLAKE8) . --exclude $(VENV) & $(MYPY) . $(MYPY_FLAGS) --exclude $(VENV) --strict