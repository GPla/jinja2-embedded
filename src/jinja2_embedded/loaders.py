import importlib.util
from importlib import import_module
from importlib.abc import ResourceReader
from typing import Callable
from typing import Tuple

from jinja2 import Environment
from jinja2 import TemplateNotFound
from jinja2.loaders import BaseLoader
from jinja2.loaders import split_template_path


__all__ = [
    'EmbeddedPackageLoader',
]


class EmbeddedPackageLoader(BaseLoader):
    """Load templates from a module in a Python package. This implementation
    uses the `Loader` and `ResourceReader` of the package provided through
    importlib to locate and load resources. Thus, making it compatible with
    bundlers like PyOxidizer, which provide their own implementations of these
    interfaces.

    Args:
        package (str): Import name of the package that contains the template
          directory, e.g., "module.templates". The templates directory must
          contain a __init__.py to qualify it as a module.
        encoding (str, optional): Encoding of the template files.
          Defaults to "utf-8".
    """

    def __init__(
        self,
        package: str,
        encoding: str = 'utf-8',
    ) -> None:
        self.package = package
        self.encoding = encoding

        # Make sure the package exists
        try:
            import_module(package)
        except ModuleNotFoundError as e:
            raise ValueError(
                f'Cannot import module "{package}". '
                'Are you missing __init__.py? '
                f'An __init__.py is only required in "{package}", '
                'but we tolerate __init__.py in subdirectories/submodules. '
            ) from e

        spec = importlib.util.find_spec(package)
        assert (
            spec is not None
        ), 'An import spec was not found for the package.'
        loader = spec.loader
        assert loader is not None, 'A loader was not found for the package.'
        self._loader = loader

    def get_source(
        self,
        environment: Environment,
        template: str,
    ) -> Tuple[str, str | None, Callable[[], bool] | None]:
        """Reads template from source.

        Args:
            environment (Environment): Environment.
            template (str): Name of template (separated by /).

        Raises:
            TemplateNotFound: Raised if the template was not found or could
              not be loaded.

        Returns:
            Tuple[str, str | None, Callable[[], bool] | None]: Returns the
              source, the path, and a callable to check if the content is
              up to date.
        """

        parts = split_template_path(template)
        path = '/'.join(parts)

        resource_reader: ResourceReader = self._loader.get_resource_reader(  # type: ignore[attr-defined]
            self.package
        )

        if resource_reader is None:
            raise TemplateNotFound(
                template,
                'Could not create ResourceReader.',
            )

        try:
            # check if we can find in resource reader of root
            # if yes, then file either in root or in subdir without __init__.py
            with resource_reader.open_resource(path) as resource:
                source = resource.read()
        except FileNotFoundError as e:
            if len(parts) < 2:
                raise TemplateNotFound(template) from e

            try:
                resource_reader = self._loader.get_resource_reader(  # type: ignore[attr-defined]
                    '.'.join([self.package, *parts[:-1]])
                )
            except ImportError as e:
                raise TemplateNotFound(template) from e

            if resource_reader is None:
                raise TemplateNotFound(
                    template,
                    'Could not create ResourceReader.',
                )

            try:
                # check if we can find the file in a submodule
                # submodule = directory with __init__.py
                with resource_reader.open_resource(parts[-1]) as resource:
                    source = resource.read()
            except FileNotFoundError as ex:
                raise TemplateNotFound(template) from ex

        return source.decode(self.encoding), path, lambda: True
