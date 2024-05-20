.DEFAULT_GOAL: help

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  test       Run schema validation on YAML files"

test:
	find features_data -type f -iname "*.yaml" -exec python validators/schema_validator.py {} +