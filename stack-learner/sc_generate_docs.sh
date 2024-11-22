#!/bin/bash
pip3 install -r src/requirements.txt    

sphinx-apidoc -o docs/source/ src/
sphinx-build -b html docs/source/ docs/build/html

cd docs/build/html
sed -i -- 's/_static/static/g' *.html     
mv _static static