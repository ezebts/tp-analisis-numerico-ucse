include scripts/tailwindcss.mk

dev:
	make tailwindcss-watch &
	uvicorn app.server:app --reload --port 8000

tests:
	python -m pytest
