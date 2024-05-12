VERSION = "0.1.0"
APP_NAME = "embedded_jinja2"
DISPLAY_NAME = "embedded_jinja2"
AUTHOR = "Gorden Platz"

def make_exe():
    dist = default_python_distribution()

    policy = dist.make_python_packaging_policy()
    policy.set_resource_handling_mode("classify")
    policy.resources_location = "in-memory"

    python_config = dist.make_python_interpreter_config()

    # start server
    python_config.run_command = "import pytest; pytest.main(['--import-mode=importlib', '-v', '-s', '../../../../tests'])"

    # include project files and install dependencies
    exe = dist.to_python_executable(
        name=APP_NAME,
        packaging_policy=policy,
        config=python_config,
    )

    for resource in exe.pip_install(["pytest"]):
        resource.add_location = "filesystem-relative:lib"
        exe.add_python_resource(resource)

    for resource in exe.pip_install([".", "./tests/test_module"]):
        resource.add_location = "in-memory"
        exe.add_python_resource(resource)

    return exe

def make_embedded_resources(exe):
    return exe.to_embedded_resources()


def make_install(exe):
    files = FileManifest()

    files.add_python_resource(".", exe)

    return files

# Tell PyOxidizer about the build targets defined above.
register_target("exe", make_exe)
register_target("install", make_install, depends=["exe"], default=True)

# Resolve whatever targets the invoker of this configuration file is requesting
# be resolved.
resolve_targets()
