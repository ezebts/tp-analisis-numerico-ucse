INPUT := $(shell pwd)/app/static/tailwind/input.css
OUTPUT := $(shell pwd)/app/static/dist/css/styles.css

.PHONY: tailwindcss-build tailwindcss-watch

tailwindcss-build:
	.tools/tailwindcss -i $(INPUT) -o $(OUTPUT) --minify

tailwindcss-watch:
	.tools/tailwindcss -i $(INPUT) -o $(OUTPUT) --watch
