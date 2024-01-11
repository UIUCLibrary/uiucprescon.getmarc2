from setuptools import setup

setup(
    packages=['uiucprescon.getmarc2'],
    test_suite="tests",
    namespace_packages=["uiucprescon"],
    tests_require=['pytest'],
    package_data={
        "uiucprescon.getmarc2": [
            "MARC21slim.xsd",
            "955_template.xml",
            "py.typed"
        ]
    },
    install_requires=[
        "lxml<5.1.0; sys_platform == 'darwin' and python_version == '3.8' and platform_machine == 'arm64'",
        "lxml; sys_platform != 'darwin' or python_version != '3.8' or platform_machine != 'arm64'",
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
