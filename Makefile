.PHONY: test format format-check
test:
	uv run --locked python scripts/test.py

format:
	git ls-files -z -- '*.py' | xargs -0 uv run --locked black

format-check:
	git ls-files -z -- '*.py' | xargs -0 uv run --locked black --check
