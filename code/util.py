from difflib import SequenceMatcher
import hashlib
import logging
from pathlib import Path
from string import Template
import pandas as pd
import traceback
import os
import json

# since measure_info files have two different formats, use recursion to look for measure_table is version agnostic
def _finditems(obj, key):
    if key in obj:
        return [obj[key]]
    items = []
    for k, v in sorted(obj.items()):
        if isinstance(v, dict):
            item = _finditems(v, key)
            if item is not None:
                items.extend(item)
    return items


def similar(a, b):
    # Checking for string similarity
    return SequenceMatcher(None, a, b).ratio()


def get_md5(filepath):
    return hashlib.md5(open(filepath, "rb").read()).hexdigest()
