# whatlang - build, test and install (BCS1212)

PREFIX  ?= /usr/local
BINDIR  ?= $(PREFIX)/bin
MANDIR  ?= $(PREFIX)/share/man/man1
COMPDIR ?= /etc/bash_completion.d
DESTDIR ?=

CFLAGS  ?= -O2 -Wall -Wextra
LDFLAGS ?=

# Directory of this Makefile (trailing slash). Anchors source paths so
# 'make' works regardless of invoking CWD.
srcdir := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
BUILD  := $(srcdir)build

.PHONY: all build install uninstall check test clean model help

all: help

build: $(srcdir)whatlang

$(BUILD)/model.bin: $(srcdir)model/model.bin.xz
	@install -d $(BUILD)
	xz -dc $< > $@.tmp
	mv $@.tmp $@

$(srcdir)whatlang: $(srcdir)whatlang.c $(BUILD)/model.bin
	$(CC) $(CFLAGS) -DMODEL_PATH='"$(BUILD)/model.bin"' -o $@ $(srcdir)whatlang.c $(LDFLAGS) -static -lm

test: build
	$(srcdir)tests/run_tests.sh $(srcdir)whatlang

# Never builds as root: run 'make build' first, then 'sudo make install'.
install:
	@test -x $(srcdir)whatlang || { echo 'whatlang: not built, run make build first' >&2; exit 1; }
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 $(srcdir)whatlang $(DESTDIR)$(BINDIR)/whatlang
	@if [ -d $(DESTDIR)$(COMPDIR) ]; then \
	  install -m 644 $(srcdir).bash_completion $(DESTDIR)$(COMPDIR)/whatlang; \
	fi
	@if [ -z "$(DESTDIR)" ]; then $(MAKE) --no-print-directory -f $(srcdir)Makefile check; fi

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/whatlang
	rm -f $(DESTDIR)$(COMPDIR)/whatlang

check:
	@command -v whatlang >/dev/null 2>&1 || { echo 'whatlang: NOT FOUND (check PATH)'; exit 1; }
	@echo 'whatlang: OK'

# Regenerate the model from py3langid (needs: pip install py3langid==0.4.0 numpy)
model:
	@install -d $(BUILD)
	python3 $(srcdir)tools/export_model.py $(BUILD)/model.bin
	xz -9e -c $(BUILD)/model.bin > $(srcdir)model/model.bin.xz

clean:
	rm -rf $(BUILD) $(srcdir)whatlang

help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@echo '  build       Compile the static whatlang binary'
	@echo '  test        Build and run the test suite'
	@echo '  install     Install to $(PREFIX) (run build first)'
	@echo '  uninstall   Remove installed files'
	@echo '  check       Verify installation'
	@echo '  model       Regenerate model/model.bin.xz from py3langid'
	@echo '  clean       Remove build output'
	@echo '  help        Show this message'
	@echo ''
	@echo 'Variables: PREFIX=$(PREFIX) BINDIR=$(BINDIR) COMPDIR=$(COMPDIR) DESTDIR=$(DESTDIR)'
