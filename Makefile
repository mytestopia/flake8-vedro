.PHONY: lint
lint:
	#python3 -m flake8 && python3 -m mypy . && python3 -m isort -m VERTICAL_HANGING_INDENT --check-only .
	python3 -m flake8 && python3 -m isort -m VERTICAL_HANGING_INDENT --check-only .

.PHONY: fix-imports
fix-imports:
	python3 -m isort -m VERTICAL_HANGING_INDENT .