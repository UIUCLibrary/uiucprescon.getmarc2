from setuptools import setup

setup(
    packages=['uiucprescon.getalmarc2'],
    test_suite="tests",
    tests_require=['pytest'],
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    package_data={
        "uiucprescon.getalmarc2": ["MARC21slim.xsd"]
    },
    install_requires=["lxml", "requests"],

)
