import sys
from argparse import ArgumentParser
from pypi2rpm.logger import get_logger

app_name = "pypi2rpm"


def main() -> int:
    logger = get_logger(app_name)
    parser = ArgumentParser()
    parser.add_argument(
        "requirement_specifier", help="PyPI (and other indexes) requirement specifier."
    )
    args = parser.parse_args()
    logger.debug("'%s' starting", __name__)
    logger.info("Processing '%s'", args.requirement_specifier)
    return 0


if __name__ == "__main__":
    sys.exit(main())
