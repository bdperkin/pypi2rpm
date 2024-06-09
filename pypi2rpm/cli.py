import sys
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "requirement_specifier", help="PyPI (and other indexes) requirement specifier."
    )
    args = parser.parse_args()
    print(args.requirement_specifier)
    return 0


if __name__ == "__main__":
    sys.exit(main())
