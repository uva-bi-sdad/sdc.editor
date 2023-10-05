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


def enforce_directory(root, dir, test):
    """
    assuming you are in a repository like data, docs, or code
    Check if "distribution" is in the folder. If not, create one and put an empty temp file in it.
    Otherwise, skip and don't do anything
    """
    # if the doc, data, or code directory does not exist, make one
    dir_path = os.path.join(root, dir)
    logging.info("Checking directory for: %s" % dir_path)

    if not os.path.isdir(dir_path):
        logging.info("\tGenerating directory %s" % dir_path)
        if not test:
            os.makedirs(dir_path)

    # if the distribution directory does not exist, make one
    sub_dir_file = os.path.join(dir_path, "distribution")
    if not os.path.isdir(sub_dir_file):
        logging.info("\t\tGenerating distribution directory: %s" % sub_dir_file)
        os.makedirs(sub_dir_file)

    # if inside there are no files, create a placeholder
    if len(os.listdir(sub_dir_file)) == 0:
        logging.info("\t\t\tGenerating placeholder empty file: %s/temp" % sub_dir_file)
        open(os.path.join(sub_dir_file, "temp"), "w").close()


@exception_handler
def generate_placeholder_folders(root_dir, test):
    """
    If a file is found under distribution, go one layer up and see if it is missing from settings.DATA_REPO_DIRS
    """
    logging.info("=" * 80)
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
                logging.info("Grandparent: %s" % grandparent_dir)
                for dir in settings.DATA_REPO_DIRS:
                    enforce_directory(grandparent_dir, dir, test)


@exception_handler
def create_placeholder_measures_info(root_dir, test):
    """
    If a file suffix is found under a distribution under a data directory and measure_info does not exist, create a temporary one
    """
    logging.info("=" * 80)
    measure_info_generated = []
    for path in Path(root_dir).rglob("data/distribution/**/*"):
        logging.info("Checking %s" % path)
        parent_dir = path.parent
        logging.debug(
            "\t[%s]: %s" % (not path.suffix in settings.SUFFIX_TO_MEASURE, path.suffix)
        )
        logging.debug(
            "\t[%s]: %s" % ("measure_info.json" in os.listdir(parent_dir), parent_dir)
        )
        if not path.suffix in settings.SUFFIX_TO_MEASURE:
            continue
        if "measure_info.json" in os.listdir(parent_dir):
            continue

        logging.debug("-" * 80)
        logging.debug("Conditions met")
        # if the file does exists but not the measure info
        scriptpath = Path(os.path.realpath(__file__))

        with open(
            os.path.join(scriptpath.parent.resolve(), "measure_info_template.json"), "r"
        ) as f:
            measure_info = json.load(f)

        df = pd.read_csv(path.resolve())
        logging.debug(df)
        logging.debug("columns: %s" % df.columns)
        logging.debug(measure_info)

        final = {}
        if "measure" in df.columns:
            measures = sorted(df["measure"].unique())
            for measure in measures:
                mi = measure_info.copy()
                mi["measure_table"] = path.name.split(".")[0]
                mi["measure"] = measure
                mi["type"] = ""
                try:
                    # because sometimes the path is empty
                    mi["type"] = df[df["measure"] == measure]["measure_type"].unique()[
                        0
                    ]
                except:
                    pass
                pprint(mi)
                final[measure] = mi
                # final.append(mi)

        export_measure_info_path = os.path.join(
            parent_dir.resolve(), "measure_info_%s.json" % mi["measure_table"]
        )
        logging.info("Placeing measure_info into %s" % export_measure_info_path)
        measure_info_generated.append(export_measure_info_path)
        if not test:
            with open(export_measure_info_path, "w") as f:
                json.dump(final, f, indent=4, sort_keys=True)
    logging.info("=" * 80)
    logging.info(
        "[%s] Measure infos generated %s"
        % (len(measure_info_generated), measure_info_generated)
    )


@exception_handler
def merge_temp_measure_infos(root_dir):
    """
    Prior measure info generates only a partial one, but they should be merged.
    Find all filespath that match the description, then group the filenames by parent path
    """
    logging.info("=" * 80)
    measure_parents = {}

    for path in Path(root_dir).rglob("data/distribution/**/*"):
        if "measure_info_" in path.name:
            if path.parent in measure_parents:
                measure_parents[path.parent].append(path)
            else:
                measure_parents[path.parent] = [path]

    for parent in measure_parents.keys():
        combined = {}
        for file in measure_parents[parent]:
            with open(file, "rb") as f:
                m = json.load(f)
            if m is None:
                continue
            for k in m.keys():
                if k in combined:
                    combined[k].append(m[k])
                else:
                    combined[k] = [m[k]]
        logging.info("-" * 80)
        logging.info(combined)

        # Save a measure_info file
        with open(os.path.join(parent, "measure_info.json"), "w") as f:
            json.dump(combined, f, indent=4, sort_keys=True)

        # Delete all key files
        for temp_measure in measure_parents.keys():
            for file in measure_parents[temp_measure]:
                filepath = file.resolve()
                os.remove(filepath)
                logging.info(
                    "[%s] Deleting %s" % (not os.path.isfile(filepath), filepath)
                )


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
    parser.add_argument("-m", "--make_measures", action=argparse.BooleanOptionalAction)
    parser.add_argument("--merge_measures", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "-g", "--generate_folders", action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-f", "--fix_measure_lists", action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-d", "--delete_empty_measures", action=argparse.BooleanOptionalAction
    )
    parser.add_argument("-t", "--test", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    if not os.path.isdir(args.input_root):
        logging.info("%s is not a directory", (args.input_root))
    else:
        logging.info("Transforming: %s", os.path.abspath(args.input_root))

        if args.fix_measure_lists:
            print("=" * 80)
            print("Fixing list measure_infos")
            fix_list_measure_infos(args.input_root, args.test)
        if args.delete_empty_measures:
            print("=" * 80)
            print("Deleting empty measure infos")
            delete_all_empty_measure_infos(args.input_root, args.test)
        if args.make_measures:
            print("=" * 80)
            print("Generating placeholder measure infos")
            create_placeholder_measures_info(args.input_root, args.test)
        if args.generate_folders:
            print("=" * 80)
            print("Enforcing folder structures")
            generate_placeholder_folders(args.input_root, args.test)
        if args.merge_measures:
            print("=" * 80)
            print("Enforcing merge measures")
            merge_temp_measure_infos(args.input_root)
