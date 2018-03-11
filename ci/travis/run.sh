# flake8 and bdist_conda test together
set -ev
if [[ "$FLAKE8" == "true" ]]; then
    flake8 .
    cp bdist_conda.py /opt/conda/lib/python${TRAVIS_PYTHON_VERSION}/distutils/command
    pushd tests/bdist-recipe && python setup.py bdist_conda && popd
    conda build --help
    conda build --version
    conda build conda.recipe --no-anaconda-upload
    conda create -n _cbtest python=$TRAVIS_PYTHON_VERSION conda-build glob2
    # because this is a file, conda is not going to process any of its dependencies.
    conda install -n _cbtest $(conda render --output conda.recipe)
    source activate _cbtest
    conda build conda.recipe --no-anaconda-upload
else
    echo "safety_checks: disabled" >> ~/.condarc
    echo "local_repodata_ttl: 1800" >> ~/.condarc
    mkdir -p ~/.conda
    conda create -n blarg1 -yq python=2.7
    conda create -n blarg2 -yq python=3.4
    conda create -n blarg3 -yq python=3.5
    conda create -n blarg4 -yq python=3.6
    conda create -n blarg5 -yq libpng=1.6.17
    /opt/conda/bin/py.test -v -n 0 --basetemp /tmp/cb --cov conda_build --cov-report xml -m "serial" tests
    /opt/conda/bin/py.test -v -n 2 --basetemp /tmp/cb --cov conda_build --cov-append --cov-report xml -m "not serial" tests --forked
fi
