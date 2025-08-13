.PHONY: scrapers-daily scrapers-bootstrap scrapers-special
scrapers-daily:
	python -m services.scraper.cli --mode daily --scope "$(SCOPE)"
scrapers-bootstrap:
	python -m services.scraper.cli --mode bootstrap --scope "$(SCOPE)" --since "$(SINCE)"
scrapers-special:
	python -m services.scraper.cli --mode special --scope "$(SCOPE)"