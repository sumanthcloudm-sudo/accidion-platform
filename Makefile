.PHONY: help verify
help:
	@echo "Targets: help verify"
verify:
	@python3 scripts/validate/repository_structure.py
