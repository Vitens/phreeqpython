import os
import sys
from pathlib import Path

from setuptools import find_packages, setup

cmdclass = {}
try:
    from wheel.bdist_wheel import bdist_wheel as _base_bdist_wheel

    class bdist_wheel(_base_bdist_wheel):
        """Always build platform wheels (never py3-none-any)."""

        def finalize_options(self):
            super().finalize_options()
            self.root_is_pure = False

    cmdclass = {"bdist_wheel": bdist_wheel}
except ImportError:  # pragma: no cover
    pass


PACKAGE_DIR = Path(__file__).parent / "phreeqpython"


def _candidate_libraries_for_target(target):
    if target == "windows":
        return ["lib/viphreeqc.dll", "lib/VIPhreeqc.dll"]
    if target == "linux":
        return ["lib/viphreeqc.so"]
    if target == "macos":
        return ["lib/viphreeqc.dylib"]
    if target == "wasm":
        return [".libs/viphreeqc.so", "lib/viphreeqcwasm.so"]
    raise ValueError("Unsupported PHREEQPYTHON_TARGET: %s" % target)


def _resolve_target():
    explicit_target = os.environ.get("PHREEQPYTHON_TARGET", "").strip().lower()
    if explicit_target:
        return explicit_target

    if sys.platform == "win32":
        return "windows"
    if "linux" in sys.platform:
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    if "emscripten" in sys.platform:
        return "wasm"
    raise RuntimeError("Unsupported platform for wheel build: %s" % sys.platform)


def _select_native_library(target):
    candidates = _candidate_libraries_for_target(target)
    for relative_path in candidates:
        if (PACKAGE_DIR / relative_path).exists():
            return relative_path
    raise FileNotFoundError(
        "No native library found for target '%s'. Expected one of: %s"
        % (target, ", ".join(candidates))
    )


TARGET = _resolve_target()
NATIVE_LIBRARY = _select_native_library(TARGET)
PACKAGE_DATA = ["database/*.dat", NATIVE_LIBRARY]


setup(
    name="phreeqpython",
    version="1.6.1",
    description="Vitens viphreeqc wrapper and utilities",
    url="https://github.com/Vitens/phreeqpython",
    author="Abel Heinsbroek",
    author_email="abel.heinsbroek@vitens.nl",
    license="Apache Licence 2.0",
    packages=find_packages(),
    package_data={"phreeqpython": PACKAGE_DATA},
    include_package_data=False,
    zip_safe=False,
    install_requires=["periodictable", "numpy"],
    extras_require={
        "kinetics": ["scipy"],
    },
    cmdclass=cmdclass,
)
