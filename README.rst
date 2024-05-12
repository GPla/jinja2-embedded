embedded-jinja2
===============

|pypi| |python| |pre-commit| |mypy| |codecov|

.. |pypi| image:: https://badge.fury.io/py/jinja2-embedded.svg
    :target: https://pypi.org/project/faster-etapr/
    :alt: Latest Version

.. |python| image:: https://img.shields.io/pypi/pyversions/jinja2-embedded
    :target: https://www.python.org/
    :alt: Supported Python Versions

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit
    :alt: Pre-Commit enabled

.. |mypy| image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/
    :alt: MyPy checked

.. |codecov| image:: https://codecov.io/gh/GPla/jinja2-embedded/graph/badge.svg?token=FVA4W2KHR4
    :target: https://codecov.io/gh/GPla/jinja2-embedded
    :alt: Code Coverage

Template loader for embedded python runtimes, e.g., `PyOxidizer <https://github.com/indygreg/PyOxidizer>`_ or `PyInstaller <https://github.com/pyinstaller/pyinstaller>`_.

The main problem with the current `PackageLoader <https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.PackageLoader>`_ is that it can only load templates from packages which are installed and materialized as directories.
However, when using a bundler from above, the resources, i.e., templates, are embedded into the executable.
Thus, the `PackageLoader` will throw the following exception: `The package was not installed in a way that PackageLoader understands`.

The `EmbeddedPackageLoader` from this package fixes this problem and required minimal changes.
Under the hood, we utilize the `Loader` and `ResourceReader` implementation of the package provided through `importlib <https://docs.python.org/3/library/importlib.html>`_.
For example, `PyOxidizer <https://github.com/indygreg/PyOxidizer>`_ implements this functionality with the `oxidized-importer <https://pypi.org/project/oxidized-importer/>`_ package.

How to use
^^^^^^^^^^

Two changes necessary.
First, change `PackageLoader` to `EmbeddedPackageLoader`:

.. code::

    from jinja2 import Environment, PackageLoader
    from jinja2_embedded import EmbeddedPackageLoader

    # before
    env = Environment(
        loader=PackageLoader('my_package', 'templates'),
    )

    # after
    env = Environment(
        loader=EmbeddedPackageLoader('my_package.templates'),
    )

    # with FastAPI
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(env=env)

Second, declare the template directory as a module by adding a `__init__.py` file:

.. code::

    my_package
    ├── __init__.py
    ├── main.py
    └── templates
        ├── __init__.py # required
        ├── bar
        │   ├── __init__.py # not required
        │   └── test.html.jinja2
        ├── foo
        │   └── test.html
        └── test.html


The subdirectories inside the template directory can be declared as modules (here `my_package.templates.bar`), but this is not required.
The `EmbeddedPackageLoader` works with either or a mixture of the two configurations.

How it works
^^^^^^^^^^^^

The `EmbeddedPackageLoader` will first try to locate the template with the `ResourceReader` from `my_package.templates`.
In our example from above, the `ResourceReader` is able to see:

.. code::

    >>> from importlib.util import find_spec
    >>> package = 'my_package.templates'
    >>> loader = find_spec(package).loader
    >>> resource_reader = loader.get_resource_reader(package)
    >>> contents = resource_reader.contents()
    >>> print(list(contents))
    ['foo/test.html', 'test.html']


So we can use the provided `resource_reader` to read either of those files:

.. code::

    >>> with resource_reader.open_resource('foo/test.html') as file:
    ...    content = file.read()
    >>> print(content.decode('utf-8'))
    FOO

Since, `bar` is declared as module, we need to use the respective `ResourceReader`:

.. code::

    >>> resource_reader = loader.get_resource_reader('my_package.templates.bar')
    >>> contents = resource_reader.contents()
    >>> print(list(contents))
    ['test.html.jinja2']

The `EmbeddedPackageLoader` will first try to find the resource in the `ResourceReader` of the main package and then fallback to the `ResourceReader` of the submodule (if it is declared as such).

Development
^^^^^^^^^^^

Install `rye <https://github.com/astral-sh/rye>`_, then run `rye sync`. This creates a `venv <https://docs.python.org/3/library/venv.html>`_ with all necessary dependencies.
Run `pytest` to run all tests.

To run the tests in a embedded Python version created with `PyOxidizer <https://github.com/indygreg/PyOxidizer>`_, run `pyoxidizer run` in the root directory.
After the executable has been build, the tests will run automatically.

This repository used `ruff <https://github.com/astral-sh/ruff>`_ to enforce style standards. The formatting is automatically done for you via `pre-commit <https://pre-commit.com/>`_.
Install pre-commit with `pre-commit install`.
