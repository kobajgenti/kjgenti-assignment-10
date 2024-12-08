# Makefile for Image Search project

# Python environment variables
CONDA_ENV_NAME = image_search
PYTHON_VERSION = 3.9
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate $(CONDA_ENV_NAME)

# Directory structure
STATIC_DIR = static
TEMPLATES_DIR = templates
UPLOAD_DIR = $(STATIC_DIR)/uploads
DEMO_DIR = $(STATIC_DIR)/demo

.PHONY: all setup clean run test dirs install-deps

# Default target
all: setup

# Create conda environment and install dependencies
setup: clean-env create-env install-deps dirs

# Create necessary directories
dirs:
	mkdir -p $(UPLOAD_DIR)
	mkdir -p $(DEMO_DIR)
	mkdir -p $(STATIC_DIR)/css
	mkdir -p $(STATIC_DIR)/js

# Create conda environment
create-env:
	conda create -n $(CONDA_ENV_NAME) python=$(PYTHON_VERSION) -y

# Install project dependencies
install-deps:
	$(CONDA_ACTIVATE) && \
	conda install numpy==1.23.5 -y && \
	conda install pytorch torchvision -c pytorch -y && \
	pip install flask && \
	pip install open-clip-torch && \
	pip install Pillow && \
	pip install pandas

# Run the Flask application
run:
	$(CONDA_ACTIVATE) && python app.py

# Clean up environment
clean-env:
	conda env remove -n $(CONDA_ENV_NAME) -y 2>/dev/null || true

# Clean up generated files and directories
clean:
	rm -rf $(UPLOAD_DIR)/*
	rm -rf __pycache__
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Clean everything including environment
clean-all: clean clean-env

# Show environment information
info:
	$(CONDA_ACTIVATE) && \
	python --version && \
	pip list

# Help target
help:
	@echo "Available targets:"
	@echo "  setup      - Create conda environment and install dependencies"
	@echo "  run        - Run the Flask application"
	@echo "  clean      - Clean up generated files"
	@echo "  clean-all  - Clean up everything including conda environment"
	@echo "  dirs       - Create necessary directories"
	@echo "  info       - Show environment information"