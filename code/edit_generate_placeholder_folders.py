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
            logging.debug("-" * 80)
            return func(*args, **kwargs)
        except Exception:
            logging.debug(traceback.format_exc())

    return wrapper


def enforce_directory(root, dir, test):
    """
    assuming you are in a repository like data, docs, or code
    Check if "distribution" is in the folder. If not, create one and put an empty temp file in it.
    Otherwise, skip and don't do anything
    """
    dirs_added = 0

    # if the doc, data, or code directory does not exist, make one
    dir_path = os.path.join(root, dir)
    logging.debug("Checking directory for: %s" % dir_path)

    if not os.path.isdir(dir_path):
        logging.debug("\tGenerating directory %s" % dir_path)
        dirs_added += 1
        if not test:
            os.makedirs(dir_path)

    # if the distribution directory does not exist, make one
    sub_dir_file = os.path.join(dir_path, "distribution")
    if not os.path.isdir(sub_dir_file):
        logging.debug("\t\tGenerating distribution directory: %s" % sub_dir_file)
        dirs_added += 1
        if not test:
            os.makedirs(sub_dir_file)

    # if inside there are no files, create a placeholder
    if os.path.isdir(sub_dir_file) and len(os.listdir(sub_dir_file)) == 0:
        logging.debug("\t\t\tGenerating placeholder empty file: %s/temp" % sub_dir_file)
        open(os.path.join(sub_dir_file, "temp"), "w").close()

    return dirs_added


@exception_handler
def generate_placeholder_folders(root_dir, test):
    """
    If a file is found under distribution, go one layer up and see if it is missing from settings.DATA_REPO_DIRS
    """
    logging.debug("=" * 80)
    total_dirs_added = 0
    for path in Path(root_dir).rglob("*/distribution/**/*"):
        for i in range(3):  # search 3 layers up
            grandparent_dir = path.parents[i].resolve()

            if (
                len(
                    set(settings.DATA_REPO_DIRS).intersection(
                        os.listdir(grandparent_dir)
                    )
                )
                > 0
            ):
                logging.debug("Grandparent: %s" % grandparent_dir)
                for dir in settings.DATA_REPO_DIRS:
                    r = enforce_directory(grandparent_dir, dir, test)
                    total_dirs_added += r
    return total_dirs_added


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Assuming you are in a repository that contains data, docs, or code directories, check if 'distribution' is in the folder. If not, create one and put an empty temp file in it. Otherwise, skip and don't do anything. At the end of this edit, there should be at least a distribution folder for each code, data, and docs folder"
    )
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
        if args.test:
            print("Directories to add: %s" % r)
        else:
            print("Directories added: %s" % r)
