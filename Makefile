PROJECT	:= backupctl
MANPAGES	:= $(PROJECT).8.gz $(PROJECT).ini.5.gz

man: $(MANPAGES)

$(PROJECT).%: $(PROJECT).%.rst
	rst2man.py $< > $@

%.gz: %
	gzip -c $< > $@

clean:
	rm -rf build/ dist/ *.egg-info $(MANPAGES) $(patsubst %.gz, %, $(MANPAGES))

test:
	isort -df -vb -ns "__init__.py" -sg "" -s "" -rc -c -p $(PROJECT) $(PROJECT)
	py.test --cov-report term-missing --cov=$(PROJECT) $(PROJECT)

rpm:
	spectool -g -R $(PROJECT).spec
	rpmbuild -ba $(PROJECT).spec
