# ? Makefile for Fly-in Project

VENV = venv

PYTHON = python3
PYTHON_PIP = ./$(VENV)/bin/python3
PIP = ./$(VENV)/bin/pip
MYPY = ./$(VENV)/bin/mypy
FLAKE8 = ./$(VENV)/bin/flake8

MAP = maps/easy/01_linear_path.txt

PROGRAM_NAME = fly-in

PDB_COMMAND = $(PYTHON_PIP) -m pdb $(PROGRAM_NAME).py

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			--disallow-untyped-defs --check-untyped-defs

LINT_COMMAND = $(FLAKE8) . --exclude $(VENV) & $(MYPY) . $(MYPY_FLAGS) --exclude $(VENV)

CREATE_VENV = $(PYTHON) -m venv $(VENV)

INSTALL_DEPS = $(PIP) install -r requirements.txt

UPDATE_PIP = $(PYTHON_PIP) -m pip install --upgrade pip

INSTALL_STAMP = .install_done

CLEAN_COMMAND = rm -rf $$(find . -name "__pycache__" -o -name ".mypy_cache") $(VENV) $(INSTALL_STAMP)

# ? Install a Python package using pip
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): requirements.txt
	@echo "Create virtual environment..."
	@$(CREATE_VENV)
	@echo "Updating pip..."
	@$(UPDATE_PIP)
	@echo "Installing dependencies..."
	@$(INSTALL_DEPS)
	@echo "Dependencies installed successfully."
	@touch $(INSTALL_STAMP)

# ? Run the program
run: install
	@clear
	@$(PYTHON_PIP) $(PROGRAM_NAME).py $(MAP)

# ? Debug the program
debug: install
	@clear
	@$(PDB_COMMAND)

# ? Clean the program
clean:
	@$(CLEAN_COMMAND)
	@echo "Program cleaned successfully."

# ? Lint the program
lint: install
	@clear
	@$(LINT_COMMAND)