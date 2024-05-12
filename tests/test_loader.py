import pytest
from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import split_template_path
from jinja2_embedded.loaders import EmbeddedPackageLoader


def test_embedded_package_loader(embedded_package_loader):
    env = Environment(loader=embedded_package_loader)
    tmpl = env.get_template('test.html')
    assert tmpl.render().strip() == 'BAR'
    pytest.raises(TemplateNotFound, env.get_template, 'missing.html')
    pytest.raises(TemplateNotFound, env.get_template, 'foo/missing.html')
    pytest.raises(TemplateNotFound, env.get_template, 'bar/missing.html')


def test_embedded_package_loader_raised():
    pytest.raises(ValueError, EmbeddedPackageLoader, 'invalid_module')


@pytest.mark.parametrize(
    ('template', 'expect'),
    [
        ('foo/test.html', 'FOO'),
        ('foo/bar/x.html', 'YYY'),
        ('bar/test.html.jinja2', 'BAR'),
        ('test.html', 'BAR'),
    ],
)
def test_embedded_package_dir_source(
    embedded_package_loader: EmbeddedPackageLoader,
    template: str,
    expect: str,
):
    source, name, up_to_date = embedded_package_loader.get_source(
        None, template
    )
    assert source.rstrip() == expect
    assert name.endswith('/'.join(split_template_path(template)))  # type: ignore
    assert up_to_date()  # type: ignore
