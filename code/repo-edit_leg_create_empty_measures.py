from dataclasses import replace
import os
import argparse
import json
import logging
from pathlib import Path
import traceback
import settings
from datetime import datetime
import util
from pprint import pprint
import pandas as pd
import os


def create_empty_measures_info(root_dir, test):
    """
    If a file suffix is found under a distribution under a data directory and measure_info does not exist, create a temporary one
    """
    logging.info("=" * 80)
    measure_info_generated = []
    for path in Path(root_dir).rglob("data/distribution/**/*"):
        logging.info("Checking %s" % path)
        parent_dir = path.parent
        logging.debug(
            "\t[%s]: %s" % (not path.suffix in settings.SUFFIX_TO_MEASURE, path.suffix)
        )
        logging.debug(
            "\t[%s]: %s" % ("measure_info.json" in os.listdir(parent_dir), parent_dir)
        )

        measure_info_path = os.path.join(parent_dir, "measure_info.json")
        # if the folder does not have anything that needs measure info of, skip it
        if not path.suffix in settings.SUFFIX_TO_MEASURE:
            continue
        if (  # if a measure info exists and its size is not zero, skip the repo
            "measure_info.json" in os.listdir(parent_dir)
            and os.stat(measure_info_path).st_size != 0
        ):
            continue

        # make an empty measure info there
        open(measure_info_path, "a").close()

        logging.debug("-" * 80)
        logging.debug("Conditions met")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UVA BI SDAD audit a Data Repository")
    parser.add_argument(
        "-i",
        "--input_root",
        type=str,
        help="The root directory that needs to be audited",
        required=True,
    )
    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction)
    parser.add_argument("-t", "--test", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    if not os.path.isdir(args.input_root):
        logging.info("%s is not a directory", (args.input_root))
    else:
        logging.info(
            "Creating empty measures for: %s", os.path.abspath(args.input_root)
        )

        print("=" * 80)
        print("Generating placeholder measure infos")
        create_empty_measures_info(args.input_root, args.test)
