"""Entry point for running as a Python executable module.

Example:
    This can be run as executable module::

        $ python -m uiucprescon.getalmarc2

"""

from uiucprescon.getalmarc2 import cli

if __name__ == '__main__':
    cli.run()
