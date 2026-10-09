PYTHON = python

.PHONY: setup pipeline dashboard test

setup:
	$(PYTHON) -m pip install -r requirements.txt

pipeline:
	$(PYTHON) load_data.py
	$(PYTHON) analysis.py

dashboard:
	$(PYTHON) -m streamlit run dashboard.py

test:
	$(PYTHON) -m pytest -q
