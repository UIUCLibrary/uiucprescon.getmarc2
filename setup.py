from setuptools import setup

setup(
    packages=['uiucprescon.getalmarc2'],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
)
