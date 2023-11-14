from dataclasses import replace
import os
import argparse
import json
import logging
from pathlib import Path
import traceback
import settings
from datetime import datetime
from util import exception_handler
from pprint import pprint
import pandas as pd
import os
import sys
import urllib.request
import pathlib
from tqdm import tqdm
import requests


def check_standard_filename(filename):
    # To do
    return False


def get_standard_filename(df, filename):
    # To do
    return None


def alter_file_name(root_dir, standard_cols):
    j = []
    p = sorted(
        list(pathlib.Path(root_dir).glob("**/distribution/*.csv.xz"))
        + list(pathlib.Path(root_dir).glob("**/distribution/*.csv"))
    )
    pbar = tqdm(p)
    for file in pbar:
        try:
            df = pd.read_csv(file, dtype={"geoid": object})
            assert set(standard_cols).issubset(df.columns)

            if not check_standard_filename(file.name):
                standard_filename = get_standard_filename(df, file.name)
                df.to_csv(
                    os.path.join(file.parent.resolve(), standard_filename), index=False
                )

        except Exception as e:
            continue
    return j


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a directory, recursively search down to find data files and change the file name based on our existing convention. Do not change if files do not match the existing format"
    )
    parser.add_argument(
        "-i",
        "--input_root",
        type=str,
        help="The root directory of files that need to be edited",
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

    standard_cols = requests.get(settings.COLUMN_REF_URL).json()
    logging.debug(standard_cols)
    j = alter_file_name(args.input_root, standard_cols)
