"""Entry point for running as a Python executable module.

Example:
    This can be run as executable module::

        $ python -m uiucprescon.getmarc2

"""

from uiucprescon.getmarc2 import cli


def main() -> None:
    """Works as the main execution point."""
    cli.run()


if __name__ == '__main__':
    main()
