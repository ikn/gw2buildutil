project_name := gw2buildutil
prefix := /usr/local
datarootdir := $(prefix)/share
docdir := $(datarootdir)/doc/$(project_name)

INSTALL_DATA := install -m 644

.PHONY: all clean distclean install uninstall

all:
	python3 setup.py bdist

clean:
	$(RM) -r build/ dist/ "$(project_name).egg-info/"
	$(RM) -r doc/_build/

distclean: clean
	find "$(project_name)" -type d -name '__pycache__' | xargs $(RM) -r

install:
	python3 setup.py install --root="$(or $(DESTDIR),/)" --prefix="$(prefix)"
	mkdir -p "$(DESTDIR)$(docdir)/"
	$(INSTALL_DATA) README.md "$(DESTDIR)$(docdir)/"

uninstall:
	./uninstall "$(DESTDIR)" "$(prefix)"
	$(RM) -r "$(DESTDIR)$(docdir)/"
