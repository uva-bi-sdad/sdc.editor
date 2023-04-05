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
import urllib.request


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            logging.debug("-" * 80)
            return func(*args, **kwargs)
        except Exception:
            logging.debug(traceback.format_exc())

    return wrapper

@exception_handler
def add_measure_info_key(root_dir, req_keys):
    """
    Add test key to each measure_info.json file
    """
    logging.debug("=" * 80)

    # CHECK EACH DATA/DISTRIBUTION FILE ------------------------
        
    for path in Path(root_dir).rglob("data/distribution/**/*"):
        logging.debug("\tEvaluating: %s" % path.name)

        if not os.path.isfile(path):
            # if path is not a file, skip to the next file to check
            continue
                
        full_path = path.name
            
        if full_path not in ["measure_info.json"]:
            # if file is not a measure info file, skip to next
            continue

        # execute these statements for measure info files
            
        with open(path.resolve(), 'r') as f:
            mi = json.load(f)
       
        # get measure info keys for each variable

        for var in mi.keys():
                
            # skip references entries
            if var == "_references":
                continue
            
            # add key
            mi[var]['test_key'] = 'test_value'                

        # write back  
        with open(path.resolve(), 'w') as f:
            json.dump(mi, f)

    return 


if __name__ == "__main__":
    
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/uva-bi-sdad/data_repo_structure/main/measure_structure.json"
    ) as url:
        req_keys = json.load(url)
    
    
    parser = argparse.ArgumentParser(
        description="Given a directory, adds a test key to each measure_info.json in a data/distribution folder."
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
        add_measure_info_key(args.input_root, req_keys)

