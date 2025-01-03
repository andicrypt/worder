.PHONY: setup full2 full3 full4 full5 full6 full7 full8 full9

# Path to the Python script
PYTHON_SCRIPT := python3 main.py

setup:
	@echo "Setting up the virtual environment..."
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@echo "Virtual environment created (if not already present)."
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Environment setup complete. Use 'source venv/bin/activate' to activate the virtual environment."


# Rules for each full dataset
full2:
	$(PYTHON_SCRIPT) --path resources/gre/full2/full2_enhanced.ods

full3:
	$(PYTHON_SCRIPT) --path resources/gre/full3/full3_enhanced.ods

full4:
	$(PYTHON_SCRIPT) --path resources/gre/full4/full4_enhanced.ods

full5:
	$(PYTHON_SCRIPT) --path resources/gre/full5/full5_enhanced.ods

full6:
	$(PYTHON_SCRIPT) --path resources/gre/full6/full6_enhanced.ods

full7:
	$(PYTHON_SCRIPT) --path resources/gre/full7/full7_enhanced.ods

full8:
	$(PYTHON_SCRIPT) --path resources/gre/full8/full8_enhanced.ods

full9:
	$(PYTHON_SCRIPT) --path resources/gre/full9/full9_enhanced.ods

gre: 
	$(PYTHON_SCRIPT) --path resources/gre/full/full.ods
