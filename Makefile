sources = NetBox Config Diff Plugin

.PHONY: test format lint unittest pre-commit clean
test: format lint unittest

format:
	black $(sources) tests

lint:
	ruff $(sources) tests

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site
