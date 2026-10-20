PYTHON ?= python3

.PHONY: test format format-check
test:
	"$(PYTHON)" scripts/test.py

format:
	git ls-files -z -- '*.py' | xargs -0 "$(PYTHON)" -m black

format-check:
	git ls-files -z -- '*.py' | xargs -0 "$(PYTHON)" -m black --check
