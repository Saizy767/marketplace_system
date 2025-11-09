test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/unit/ -v

test-int:
	python -m pytest tests/integrations/ -v