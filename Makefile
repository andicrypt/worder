.PHONY: full2 full3 full4 full5 full6 full7 full8 full9

# Path to the Python script
PYTHON_SCRIPT := python3 main.py

# Rules for each full dataset
full2:
	$(PYTHON_SCRIPT) --path ../full2/full2_enhanced.ods

full3:
	$(PYTHON_SCRIPT) --path ../full3/full3_enhanced.ods

full4:
	$(PYTHON_SCRIPT) --path ../full4/full4_enhanced.ods

full5:
	$(PYTHON_SCRIPT) --path ../full5/full5_enhanced.ods

full6:
	$(PYTHON_SCRIPT) --path ../full6/full6_enhanced.ods

full7:
	$(PYTHON_SCRIPT) --path ../full7/full7_enhanced.ods

full8:
	$(PYTHON_SCRIPT) --path ../full8/full8_enhanced.ods

full9:
	$(PYTHON_SCRIPT) --path ../full9/full9_enhanced.ods

learnt: 
	$(PYTHON_SCRIPT) --path ../learnt/learnt.ods

journal:
	$(PYTHON_SCRIPT) --path ../journal/journal.ods
	
combine:
	$(PYTHON_SCRIPT) --path ../learnt/learnt.ods ../journal/journal.ods

shuffle:
	$(PYTHON_SCRIPT) --path ../learnt/shuffle/learnt.ods