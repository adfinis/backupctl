PROJECT := bkpmgmt

man: bkpmgmt.8

bkpmgmt.8: README.rst
	rst2man.py $< > $@

clean:
	rm -rf build/ dist/ *.egg-info

test:
	isort -df -vb -ns "__init__.py" -sg "" -s "" -rc -c -p bkpmgmt bkpmgmt
	py.test --cov-report term-missing --cov=bkpmgmt bkpmgmt
