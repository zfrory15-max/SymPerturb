.PHONY: test example clean

test:
	PYTHONPATH=src pytest

example:
	PYTHONPATH=src python -m symperturb.cli \
		--data examples/synthetic_symptoms.csv \
		--modules examples/modules.csv \
		--anchors examples/anchors.csv \
		--config examples/config.yaml \
		--out example-output

clean:
	rm -rf example-output .pytest_cache **/__pycache__
