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


def generate_link_json(root_dir, cols):
    j = []
    p = sorted(
        list(pathlib.Path(root_dir).glob("**/distribution/*.csv.xz"))
        + list(pathlib.Path(root_dir).glob("**/distribution/*.csv"))
    )
    pbar = tqdm(p)
    for file in pbar:
        try:
            df = pd.read_csv(file)
            assert set(cols).issubset(df.columns)
            last_mod_time = datetime.utcfromtimestamp(os.path.getmtime(file)).strftime(
                "%Y-%m-%d_%H:%M:%S"
            )
            # print("Saving %s: %s" % (str(file), last_mod_time))
            j.append({"path": str(file), "last_modified_utc": last_mod_time})
        except Exception as e:
            continue
    return j


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given a directory, recursively search down to find csvs and save their relative link as a json file"
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

    anticipated_cols = requests.get(
        "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/column_structure.json"
    ).json()
    logging.debug(anticipated_cols)
    j = generate_link_json(args.input_root, anticipated_cols)

    pprint(j)
    print(len(j))
    with open(os.path.join(args.input_root, ".valid_csv_links"), "w") as f:
        json.dump(j, f, indent=4)
