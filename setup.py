import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_version():
    # workaround to resolve import issue
    basedir = os.path.dirname(os.path.realpath(__file__))
    version_line = None
    with open(os.path.join(basedir, "settrie.py")) as fp:
        for line in fp:
            if line.startswith("__version__"):
                version_line = line
                break

    l_quote = version_line.find('"')
    r_quote = version_line.rfind('"')
    return version_line[l_quote + 1 : r_quote]


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            "--cov",
            "settrie",
            "--cov-report",
            "term-missing",
            "test.py",
        ]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="settrie",
    version=get_version(),
    description="A trie data struct that is designed for set.",
    author="tzing",
    author_email="tzingshih@gmail.com",
    py_modules=["settrie"],
    python_requires=">=3.5",
    tests_require=["pytest", "pytest-cov"],
    cmdclass={"test": PyTest},
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
    ],
)
