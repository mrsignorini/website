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

.PHONY: default start start-watch watch build clean
