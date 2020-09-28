project_name := gw2buildutil

INSTALL_DATA := install -m 644

prefix := /usr/local

.PHONY: all clean install uninstall

all:
	python3 setup.py bdist

clean:
	find "$(project_name)" -type d -name '__pycache__' | xargs $(RM) -r
	$(RM) -r build/ dist/ "$(project_name).egg-info/"
	$(RM) -r doc/_build/

install:
	python3 setup.py install --root="$(or $(DESTDIR),/)" --prefix="$(prefix)"
	mkdir -p "$(DESTDIR)$(docdir)/"
	$(INSTALL_DATA) README.md "$(DESTDIR)$(docdir)/"

uninstall:
	./uninstall "$(DESTDIR)" "$(prefix)"
	$(RM) -r "$(DESTDIR)$(docdir)/"
