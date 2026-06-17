default: start

HUGO ?= hugo
HUGO_SERVER_FLAGS ?= --watch=true --disableFastRender
HUGO_BUILD_FLAGS ?= --minify

start:
	$(HUGO) server $(HUGO_SERVER_FLAGS)

start-watch: start

watch: start

build:
	$(HUGO) $(HUGO_BUILD_FLAGS)

clean:
	rm -rf public resources .hugo_build.lock

publish:
	$(HUGO) $(HUGO_BUILD_FLAGS) --destination docs
	touch docs/.nojekyll
	git add docs/
	git commit -m "Publish $$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
	git push origin main

.PHONY: default start start-watch watch build clean publish
