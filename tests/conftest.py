import pytest
from jinja2_embedded import loaders


@pytest.fixture
def embedded_package_loader() -> loaders.EmbeddedPackageLoader:
    """
    Returns:
        loaders.EmbeddedPackageLoader: Returns an embedded package loader
          initialized from templates.
    """
    return loaders.EmbeddedPackageLoader('test_module.templates')
