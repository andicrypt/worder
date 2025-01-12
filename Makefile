.PHONY: setup sub1 sub2 sub3 sub4 sub5 sub6 sub7 sub8 full

# Path to the Python script
PYTHON_SCRIPT := python3 main.py

setup:
	@echo "Setting up the virtual environment..."
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@echo "Virtual environment created (if not already present)."
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Environment setup complete. Use 'source venv/bin/activate' to activate the virtual environment."


# Rules for each sub dataset

sub1:
	$(PYTHON_SCRIPT) --path resources/gre/sub1.ods

sub2:
	$(PYTHON_SCRIPT) --path resources/gre/sub2.ods

sub3:
	$(PYTHON_SCRIPT) --path resources/gre/sub3.ods

sub4:
	$(PYTHON_SCRIPT) --path resources/gre/sub4.ods

sub5:
	$(PYTHON_SCRIPT) --path resources/gre/sub5.ods

sub6:
	$(PYTHON_SCRIPT) --path resources/gre/sub6.ods

sub7:
	$(PYTHON_SCRIPT) --path resources/gre/sub7.ods

sub8:
	$(PYTHON_SCRIPT) --path resources/gre/sub8.ods

full: 
	$(PYTHON_SCRIPT) --path resources/gre/full.ods
