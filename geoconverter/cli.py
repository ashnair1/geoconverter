"""Command-line interface for geoconverter."""

import sys

from geoconverter.gdal_convert import get_args
from geoconverter.gdal_convert import main as gdal_main


def main() -> None:
    """Main CLI entry point for geoconverter."""
    try:
        args = get_args()
        gdal_main(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
