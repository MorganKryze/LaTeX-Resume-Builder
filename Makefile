# Resume-LaTeX template — Makefile
# All targets respect the CONFIG and PROJECT_ROOT variables so the same Makefile
# can be invoked from a consumer (private) repo via `make -C template …`.

CONFIG       ?= options.example.yml
PROJECT_ROOT ?= .
BUILD_DIR    ?= build
UV           ?= uv

.PHONY: all install build merge qr test lint clean help

all: build merge qr ## Build everything (compile LaTeX, merge, QR)

install: ## Sync Python deps via uv; warn about missing system tools
	$(UV) sync
	@command -v latexmk  >/dev/null || echo "WARN: latexmk not on PATH — install TeX Live"
	@command -v pdftoppm >/dev/null || echo "WARN: pdftoppm not on PATH — install poppler"

build: ## Compile all LaTeX resumes declared in $(CONFIG)
	@mkdir -p $(BUILD_DIR)
	$(UV) run python scripts/compile_latex.py --config $(CONFIG) --project-root $(PROJECT_ROOT)

merge: ## Convert PDFs to JPG + merge per $(CONFIG)
	$(UV) run python scripts/convert_and_merge.py --config $(CONFIG) --project-root $(PROJECT_ROOT)

qr: ## Generate the QR code per $(CONFIG)
	$(UV) run python scripts/generate_qr_code.py --config $(CONFIG) --project-root $(PROJECT_ROOT)

test: ## Run unit tests
	$(UV) run python -m unittest tests.tests -v

lint: ## Run ruff + black (check-only)
	$(UV) run ruff check .
	$(UV) run black --check .

clean: ## Remove build artifacts
	rm -rf $(BUILD_DIR)
	find . -type f \( -name '*.aux' -o -name '*.log' -o -name '*.synctex.gz' \
	  -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.out' \
	  -o -name '*.toc' \) -delete

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Targets:\n"} \
	  /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
