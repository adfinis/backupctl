PROJECT := backupctl

man: backupctl.8

$(PROJECT).8: README.rst
	rst2man.py $< > $@

clean:
	rm -rf build/ dist/ *.egg-info

test:
	isort -df -vb -ns "__init__.py" -sg "" -s "" -rc -c -p $(PROJECT) $(PROJECT)
	py.test --cov-report term-missing --cov=$(PROJECT) $(PROJECT)
