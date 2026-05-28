VENV   = build/.venv
PYTHON = $(VENV)/bin/python3
PIP    = $(VENV)/bin/pip

$(VENV): FORCE
	python3 -m venv $(VENV)
	$(PIP) install --quiet commonmark

build: $(VENV)
	$(PYTHON) build/makesite.py

serve: build
	@echo "Serving at http://localhost:8000"
	$(PYTHON) -m http.server --directory _site

test: $(VENV)
	PYTHONPATH=build $(PYTHON) -m unittest discover -s build/test -v

clean:
	rm -rf _site
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm {} +

FORCE:
