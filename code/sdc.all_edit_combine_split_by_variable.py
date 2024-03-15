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


def export_variable_csvs(root_dir, export_dir, expected_col_order):
    j = []
    p = sorted(
        list(pathlib.Path(root_dir).glob("**/distribution/*.csv.xz"))
        + list(pathlib.Path(root_dir).glob("**/distribution/*.csv"))
    )
    pbar = tqdm(p)
    dfs = []
    variables = set()
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
            if len(df["measure"].unique()) > 1:
                logging.info("[%s]: %s" % (file.name, len(df["measure"].unique())))

            # Checking if the assumption that variables are unique by file
            variable_set = set(df["measure"].unique())
            if len(variables.intersection(variable_set)) > 0:
                logging.info(
                    "Existing variables! %s" % variables.intersection(variable_set)
                )
            variables |= variable_set
            df = df[expected_col_order]  # only store required columns for these sets
            dfs.append(df)

        except Exception as e:
            logging.error("Edit failed: %s, %s" % (file, traceback.format_exc()))
            continue

    fdf = pd.concat(dfs)
    print(fdf)
    logging.info("File table length: %s" % len(fdf))
    pbar = tqdm(fdf["measure"].unique())

    L = [x for i, x in fdf.groupby(by="measure", sort=False)]

    for pdf in tqdm(L):
        export_path = os.path.join(
            export_dir,
            "{measure_name}.zip".format(measure_name=pdf["measure"].values[0]),
        )
        pdf.to_csv(export_path, index=False)
    # for m in pbar:
    #     pdf = fdf[fdf["measure"] == m]
    #     fdf = fdf[fdf["measure"] != m]  # remove the rest from the equation
    #     pdf = pdf.dropna(
    #         subset=["year", "geoid"], how="any"
    #     )  # if we are missing things on any, we drop it
    #     export_path = os.path.join(
    #         export_dir, "{measure_name}.csv.xz".format(measure_name=m)
    #     )
    #     pdf.to_csv(export_path, index=False)
    #     pbar.set_description("Saving: %s" % m)


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
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="The directory of files that need to be exported",
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

    assert os.path.isdir(args.output_dir), logging.info(
        "%s is not a directory", (args.output_dir)
    )

    anticipated_cols = requests.get(settings.COLUMN_REF_URL).json()
    # anticipated_cols.remove("moe")
    logging.info(anticipated_cols)
    j = export_variable_csvs(args.input_root, args.output_dir, anticipated_cols)
