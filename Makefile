# ? Makefile for Fly-in Project

VENV = venv

PYTHON = python3
PIP = ./$(VENV)/bin/pip
MYPY = ./$(VENV)/bin/mypy
FLAKE8 = ./$(VENV)/bin/flake8

FILE_NAME_MAP = maps/easy/01_linear_path.txt

PROGRAM_NAME = fly-in

PDB_COMMAND = $(PYTHON) -m pdb $(PROGRAM_NAME).py

CLEAN_COMMAND = rm -rf $$(find . -name "__pycache__" -o -name ".mypy_cache") $(VENV)

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			--disallow-untyped-defs --check-untyped-defs

LINT_COMMAND = $(FLAKE8) . --exclude $(VENV) & $(MYPY) . $(MYPY_FLAGS) --exclude $(VENV)

CREATE_VENV = $(PYTHON) -m venv $(VENV)

INSTALL_DEPS = $(PIP) install -r requirements.txt

# ? Install a Python package using pip
install:
	@echo "Create virtual environment..."
	@$(CREATE_VENV)
	@echo "Installing dependencies..."
	@$(INSTALL_DEPS)
	@echo "Dependencies installed successfully."

# ? Run the program
run:
	@$(PYTHON) $(PROGRAM_NAME).py $(FILE_NAME_MAP)

# ? Debug the program
debug:
	@$(PDB_COMMAND)

# ? Clean the program
clean:
	@$(CLEAN_COMMAND)
	@echo "Program cleaned successfully."

# ? Lint the program
lint:
	@$(LINT_COMMAND)

# ? Lint strict the program
lint-strict:
	@$(FLAKE8) . --exclude $(VENV) & $(MYPY) . $(MYPY_FLAGS) --exclude $(VENV) --strict