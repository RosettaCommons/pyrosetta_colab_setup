# pyrosetta_colab_setup
Files for our auxiliary pyrosetta_colab_setup PyPI package

## How to build package for release and upload to PyPI
1. Change version number in `setup.py`
2.
```
pip install --user --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
python -m twine upload dist/*
```
