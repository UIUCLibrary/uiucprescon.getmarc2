from setuptools import setup

setup(
    packages=['uiucprescon.getmarc2'],
    test_suite="tests",
    tests_require=['pytest'],
    namespace_packages=["uiucprescon"],
    setup_requires=['pytest-runner'],
    package_data={
        "uiucprescon.getmarc2": ["MARC21slim.xsd"]
    },
    install_requires=["lxml", "requests"],
    entry_points={
        "console_scripts": [
            "getmarc = uiucprescon.getmarc2.__main__:main"
        ]
    }

)
