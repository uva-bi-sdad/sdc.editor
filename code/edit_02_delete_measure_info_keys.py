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
def delete_measure_info_keys(root_dir, req_keys):
    """
    Delete extra keys in each measure_info.json file
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

            # check for extra keys
            extra_keys = list(set(key_list).difference(set(req_keys)))

            if len(extra_keys) > 0:
                # delete extra keys
                for i in range(len(extra_keys)):
                    mi[var].pop(extra_keys[i])

                # sort keys
                updated_keys = list(set(key_list).difference(set(extra_keys)))
                updated_keys.sort()
                sorted_dict = {i: mi[var][i] for i in updated_keys}
                mi[var] = sorted_dict

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

    parser = argparse.ArgumentParser(
        description="Given a directory, deletes extra keys in each measure_info.json in a data/distribution folder."
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
        delete_measure_info_keys(args.input_root, req_keys)
