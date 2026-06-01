#!/usr/bin/env python3

import argparse
import logging
import sys
from os.path import isdir, isfile, join, basename, exists
from os import makedirs

from evtx_miner.convert import convert_evtx_directory, convert_evtx_file

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convert Windows EVTX files to JSONL format"
    )

    parser.add_argument(
        "input",
        help="Path to an EVTX file or a directory containing EVTX files",
    )

    parser.add_argument(
        "output",
        help="Output directory (or output file if input is a single EVTX file)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    input_path = args.input
    output_path = args.output

    if not exists(input_path):
        parser.error(f"Input path does not exist: {input_path}")
        sys.exit(2)

    if isdir(input_path):
        logger.info(f"Processing EVTX directory: {input_path}")
        if not exists(output_path):
            makedirs(output_path)
        elif isfile(output_path):
            logger.error(f"Input path is a directory and output path is a file: {input_path=} {output_path=}")
            sys.exit(3)
        elif isdir(output_path) and not args.force:
            logger.warning(f"Output directory already exist: {output_path=}, use -f or --force to ignore this warning!")
            sys.exit(4)
        convert_evtx_directory(input_path, output_path)

    elif isfile(input_path):
        logger.info(f"Processing single EVTX file: {input_path}")

        # If output is a directory, derive output filename automatically
        if output_path.endswith("/") or not output_path.lower().endswith(".jsonl"):
            output_file = join(
                output_path,
                basename(input_path) + ".jsonl",
            )
        else:
            output_file = output_path

        if exists(output_file):
            logger.warning(f"Output file already exist: {output_file=}, use -f or --force to ignore this warning!")
            sys.exit(4)

        convert_evtx_file(input_path, output_file)


if __name__ == "__main__":
    main()
