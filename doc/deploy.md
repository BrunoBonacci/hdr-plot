# deploy

``` bash
pip install wheel
pip install twine
rm -fr dist/ hdr_plot.egg-info/ build/ .eggs/

# TEST BUILD

# build dist
python3 setup.py sdist bdist_wheel

export TWINE_USERNAME='xxx'
export TWINE_PASSWORD='yyy'

twine upload -r testpypi dist/*

pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://testpypi.python.org/pypi --user --upgrade hdr-plot

hdr-plot --output myplot.png --title "My plot" ./sample/file1.out ./sample/file2.out ./sample/file3.out

pip3 uninstall -y hdr-plot


# FINAL BUILD
export TWINE_USERNAME='xxx2'
export TWINE_PASSWORD='yyy2'

twine upload dist/*

```
