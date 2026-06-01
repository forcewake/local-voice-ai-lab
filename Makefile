.PHONY: setup voxtral qwen3-clone higgs-clone parakeet smoke all report publish-check clean-reports

PYTHON ?= .venv/bin/python

setup:
	uv venv --python 3.12 --seed
	.venv/bin/python -m pip install -U -e ".[all]"

voxtral:
	$(PYTHON) scripts/voice_lab.py voxtral

qwen3-clone:
	$(PYTHON) scripts/voice_lab.py qwen3-clone

higgs-clone:
	$(PYTHON) scripts/voice_lab.py higgs-clone

parakeet:
	$(PYTHON) scripts/voice_lab.py parakeet

smoke:
	$(PYTHON) scripts/voice_lab.py suite --suite smoke

all:
	$(PYTHON) scripts/voice_lab.py suite --suite all

report:
	$(PYTHON) scripts/voice_lab.py report

publish-check:
	$(PYTHON) scripts/publish_check.py

clean-reports:
	rm -rf runs artifacts audio reports/voice_lab_results.csv reports/voice_lab_report.md reports/index.html
