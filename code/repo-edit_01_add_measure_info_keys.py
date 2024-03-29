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


@exception_handler
def add_measure_info_keys(root_dir, req_keys, req_source_keys):
    """
    Add missing keys to each measure_info.json file
    """
    logging.debug("=" * 80)

    # CHECK EACH DATA/DISTRIBUTION FILE ------------------------

    for path in Path(root_dir).rglob("data/distribution/**/*"):
        logging.debug("\tEvaluating: %s" % path.name)

        if not os.path.isfile(path):
            # if path is not a file, skip to the next file to check
            continue

        if path.name not in ["measure_info.json"]:
            # if file is not a measure info file, skip to next
            continue

        # execute these statements for measure info files

        with open(path.resolve(), "r") as f:
            mi = json.load(f)

        # get measure info keys for each variable

        updated = 0  # tracks if file is updated and needs to be rewritten

        for var in mi.keys():
            # skip references entries
            if var == "_references":
                continue

            key_list = list(mi[var].keys())

            # check for missing keys
            missing_keys = list(set(req_keys).difference(set(key_list)))

            if len(missing_keys) > 0:
                # add missing keys
                for i in range(len(missing_keys)):
                    mi[var][missing_keys[i]] = ""

                # sort keys
                updated_keys = list(set(key_list).union(set(missing_keys)))
                updated_keys.sort()
                sorted_dict = {i: mi[var][i] for i in updated_keys}
                mi[var] = sorted_dict

                updated = 1

            # check for missing source keys
            sources_list = mi[var]["sources"]

            for i in range(len(sources_list)):
                source_key_list = list(mi[var]["sources"][i].keys())
                missing_source_keys = list(set(req_source_keys).difference(set(source_key_list)))

                if len(missing_source_keys) > 0:
                    # add missing keys
                    for j in range(len(missing_source_keys)):
                        mi[var]["sources"][i][missing_source_keys[j]] = ""

                    # sort source keys
                    updated_source_keys = list(set(source_key_list).union(set(missing_source_keys)))
                    updated_source_keys.sort()
                    sorted_source_dict = {j: mi[var]["sources"][i][j] for j in updated_source_keys}
                    mi[var]["sources"][i] = sorted_source_dict

                    updated = 1

        # write back updates to measure_info file
        if updated:
            with open(path.resolve(), "w") as f:
                json.dump(mi, f, indent=4)

    return


if __name__ == "__main__":
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/measure_structure.json"
    ) as url:
        req_keys = json.load(url)

    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/uva-bi-sdad/sdc.metadata/master/data/source_structure.json"
    ) as url:
        req_source_keys = json.load(url)
    
    parser = argparse.ArgumentParser(
        description="Given a directory, adds missing keys to each measure_info.json in a data/distribution folder."
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
    else:
        add_measure_info_keys(args.input_root, req_keys, req_source_keys)
