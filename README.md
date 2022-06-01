# pyrosetta_colab_setup
Files for our auxiliary pyrosetta_colab_setup PyPI package

## How to build package for release and upload to PyPI
1. Change version number in `setup.py`
```
# first run docker container
docker run -it python /bin/bash

pip install --user --upgrade setuptools wheel twine
rm dist/* ; python setup.py sdist bdist_wheel
python -m twine upload dist/*
```
