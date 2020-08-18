project_name := gw2build

INSTALL_DATA := install -m 644

prefix := /usr/local

.PHONY: all clean install uninstall

all:
	python3 setup.py bdist

clean:
	find "$(project_name)" -type d -name '__pycache__' | xargs $(RM) -r
	$(RM) -r build/ dist/ "$(project_name).egg-info/"

install:
	python3 setup.py install --root="$(or $(DESTDIR),/)" --prefix="$(prefix)"

uninstall:
	./uninstall "$(DESTDIR)" "$(prefix)"
