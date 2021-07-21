clean-pyc:
	find . -name '*.pyc' -delete

test: clean-pyc
	python3 -m unittest discover tests

plot: clean-pyc
	python3 src/plot/plot.py

main: clean-pyc
	python3 main.py

performance-measure: clean-pyc
	python3 -m src.start_scripts.performance_simple_protcols $(ARGS)
