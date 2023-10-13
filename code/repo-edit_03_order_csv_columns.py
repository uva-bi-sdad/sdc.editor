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
import pathlib
from tqdm import tqdm
import requests


def straighten_csvs(root_dir, expected_col_order):
    j = []
    p = sorted(
        list(pathlib.Path(root_dir).glob("**/distribution/*.csv.xz"))
        + list(pathlib.Path(root_dir).glob("**/distribution/*.csv"))
    )
    pbar = tqdm(p)
    for file in pbar:
        try:
            df = pd.read_csv(file, dtype={"geoid": object})
            if df.empty:  # skip empty data frames
                continue
            assert set(expected_col_order).issubset(df.columns), print(df.columns)
            if (  # Skip if columns are already in order
                list(df.columns)[: len(expected_col_order)] == expected_col_order
            ):
                pbar.set_description("Columns already in order: %s" % df.columns)
                continue

            df = df[  # re-order the columns and keep the additional ones
                expected_col_order + list(set(df.columns) - set(expected_col_order))
            ]
            assert (
                list(df.columns)[: len(expected_col_order)] == expected_col_order
            ), logging.error(list(df.columns)[: len(expected_col_order)])
            pbar.set_description("edited columns: %s" % df.columns)
            df.to_csv(file, index=False)
            logging.debug("File straightened: %s" % file)
        except Exception as e:
            logging.debug("Edit failed: %s, %s" % (file, traceback.format_exc()))
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a directory, recursively search down to find data csv files and make sure the heading order is standardized so that csvs can be joined just with text manipulation"
    )
    parser.add_argument(
        "-i",
        "--input_root",
        type=str,
        help="The root directory of files that need to be edited",
        required=True,
    )
    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    if not os.path.isdir(args.input_root):
        logging.info("%s is not a directory", (args.input_root))

    anticipated_cols = requests.get(settings.COLUMN_REF_URL).json()
    logging.info(anticipated_cols)
    j = straighten_csvs(args.input_root, anticipated_cols)
