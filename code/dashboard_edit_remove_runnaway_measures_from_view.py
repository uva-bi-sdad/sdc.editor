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


def cull_extra_measures(root_dir, expected_col_order):
    # The data columns also determine what is considered a data file versus what is not considered a data file
    j = []
    p = sorted(
        list(pathlib.Path(root_dir).glob("**/distribution/*.csv.xz"))
        + list(pathlib.Path(root_dir).glob("**/distribution/*.csv"))
    )
    pbar = tqdm(p)
    dfs = []
    all_measures = set()
    logging.info("Collecting all measures")
    for file in pbar:
        try:
            df = pd.read_csv(file, dtype={"geoid": object})
            pbar.set_description("[%s] Reading %s" % (len(dfs), file.name))
            if df.empty:  # skip empty data frames
                continue

            # Try to add in columns if there are insufficient ones
            df = df.reindex(columns=expected_col_order)

            # A dataset is only acceptable if it has a minimum number of expected columns
            assert set(expected_col_order).issubset(df.columns), print(df.columns)
            all_measures |= set(df["measure"].unique())

        except Exception as e:
            logging.error("Failed to read %s: %s" % (file, traceback.format_exc()))
            continue

    views = sorted(pathlib.Path(root_dir).glob("**/view.json"))

    for view in views:
        with open(view, "r") as f:
            j = json.load(f)
        measures = set(j["variables"])

        # all allow measures that exist
        resulting_measures = measures.intersection(all_measures)
        logging.info("Removing: %s" % (measures ^ resulting_measures))
        logging.info(
            "\tNumber of measures removed from %s: %s"
            % (view, len(measures) - len(resulting_measures))
        )
        # edit the variables list
        j["variables"] = sorted(list(measures))
        # Write the updated list back into the view.json file
        with open(view, "w") as f:
            json.dump(j, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Given the Social Data Commons structure, remove measures from view.json that do not exist anywhere inside data files. This script only looks that the measures inside the csvs, not inside the measure_info.json"
    )
    parser.add_argument(
        "-i",
        "--input_root",
        type=str,
        help="The root directory of the cloned social_data_commons folder",
        required=True,
    )

    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    assert os.path.isdir(args.input_root), logging.info(
        "%s is not a directory", (args.input_root)
    )

    anticipated_cols = requests.get(settings.COLUMN_REF_URL).json()
    # anticipated_cols.remove("moe")
    logging.info(anticipated_cols)
    j = cull_extra_measures(args.input_root, anticipated_cols)
