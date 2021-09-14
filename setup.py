from setuptools import setup

setup(
    packages=['uiucprescon.getmarc2'],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    package_data={
        "uiucprescon.getmarc2": [
            "MARC21slim.xsd",
            "955_template.xml",
            "py.typed"
        ]
    },
    install_requires=[
        "lxml",
        'importlib-metadata;python_version<"3.8"',
        'importlib-resources;python_version<"3.9"',
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "getmarc = uiucprescon.getmarc2.__main__:main"
        ]
    }

)
