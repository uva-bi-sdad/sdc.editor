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
import sys


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            print("-" * 80)
            return func(*args, **kwargs)
        except Exception:
            print(traceback.format_exc())

    return wrapper


def enforce_directory(dir_path, test, report):
    """
    assuming you are in a repository like data, docs, or code
    Check if "distribution" is in the folder. If not, create one and put an empty temp file in it.
    Otherwise, skip and don't do anything
    """

    # if the distribution directory does not exist, make one
    sub_dir_file = dir_path / "distribution"
    logging.info("Checking directory for: %s" % sub_dir_file)
    if not os.path.isdir(sub_dir_file):
        logging.debug("\t\tGenerating distribution directory: %s" % sub_dir_file)
        if not test:
            os.makedirs(sub_dir_file)
        report["dirs_created"] += 1

    # if inside there are no files, create a placeholder
    logging.debug("\t\tfile is dir: %s" % os.path.isdir(sub_dir_file))
    if os.path.isdir(sub_dir_file):
        logging.debug("\t\tlength of subdir_file: %s" % len(os.listdir(sub_dir_file)))
        logging.debug(os.listdir(sub_dir_file))

    if os.path.isdir(sub_dir_file) and len(os.listdir(sub_dir_file)) == 0:
        logging.debug("\t\t\tGenerating placeholder empty file: %s/temp" % sub_dir_file)
        if not test:
            open(os.path.join(sub_dir_file, "temp"), "w").close()
        report["files_created"] += 1
    else:
        logging.debug(
            "\t\tNot a folder or folder or folder is not empty: %s" % sub_dir_file
        )


@exception_handler
def generate_placeholder_folders(root_dir, test):
    """
    Instead of making code, data, docs for peopel (which they might not need all 3), instead just put in placeholder distribution folders, if code, data, or docs are detected, but no distribution file is shown
    """
    logging.info("=" * 80)
    report = {
        "dirs_created": 0,
        "files_created": 0,
    }
    cdd_dirs = (
        list(Path(root_dir).rglob("**/code/"))
        + list(Path(root_dir).rglob("**/data/"))
        + list(Path(root_dir).rglob("**/docs/"))
    )

    logging.debug("cdd_dirs: %s " % len(cdd_dirs))

    for dir in cdd_dirs:
        logging.debug("Parsing path match: %s" % dir)
        enforce_directory(dir, test, report)

    return report


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
        r = generate_placeholder_folders(args.input_root, args.test)
        print(r)
