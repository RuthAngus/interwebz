#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import re
import string
import tarfile
import fnmatch
import requests
import feedparser
import numpy as np
import os

URL = "http://arxiv.org/rss/astro-ph"
COMMENT_RE = re.compile(r"(?<!\\)%")
AMP_RE = re.compile(r"(?<!\\)&")

def run():
    tree = feedparser.parse(URL)
    for entry in tree.entries:
        url = entry.id.replace("/abs/", "/e-print/")
        print(url)


def extract_tables(fh):
    """
    Extracts tables from latex file and returns a list of strings.
    One string for each table.
    """
    with tarfile.open(fileobj=fh) as f:
        for mem in f.getmembers():
            if not fnmatch.fnmatch(mem.name, "*.tex"):
                continue
            with f.extractfile(mem) as txtf:
                txt = txtf.read()
            txt = txt.decode("utf-8")

            # detect table line positions
            tables = []
            lines = np.array(txt.splitlines())
            for i, line in enumerate(lines):
                if line[1:12] == "begin{table":
                    beg_ind = i
                elif line[1:10] == "end{table":
                    end_ind = i
                    tables.append(lines[beg_ind:end_ind])
    return tables

def read_table(table):
    """
    Takes a latex table as a list of strings (one per line) and extracts the
    data.
    Returns an array of data.
    SO MANY BUGS IN THIS RIGHT NOW!
    """

    data = []
    for i, line in enumerate(table):  # alternatively, detect "&"s
        if "&" in line:
            data.append(line.split("&"))  # shape: rows, columns

    column_headers = data[0]
    column_units = data[1]
    data_array = np.array(data[2:])

    # find all the floats
    numeric_const_pattern = r"""
        [-+]? # optional sign
        (?:
            (?: \d* \. \d+ ) # .1 .12 .123 etc 9.1 etc 98.1 etc
            |
            (?: \d+ \.? ) # 1. 12. 123. etc 1 12 123 etc
        )
        # followed by optional exponent part if desired
        (?: [Ee] [+-]? \d+ ) ?
        """
    rx = re.compile(numeric_const_pattern, re.VERBOSE)

    # extract the floats from a line and create an array of the data
    data_stack = []
    for row in data_array:
        float_line = []
        for entry in row:
            floats = rx.findall(entry)
            if len(floats):
                float_line.append(float(floats[0]))
            else:
                float_line.append(np.nan)
        data_stack.append(float_line)
    return np.array(data_stack), column_headers, column_units

def tex_files(members):
    for tarinfo in members:
        if os.path.splitext(tarinfo.name)[1] == ".tex":
            yield tarinfo

def load_tables(arxiv_number):
    """
    Takes an ArXiv id and returns a list of arrays.
    Each array contains the data in a table in the paper.
    """
    file = "data/{0}.tar.gz".format(str(arxiv_number))
    with open(file, "rb") as f:
        tables = extract_tables(f)
    data_list, header_list, unit_list = [], [], []
    for table in tables:
        dat, head, unit = read_table(table)
        data_list.append(dat)
        header_list.append(head)
        unit_list.append(unit)
    return data_list, header_list, unit_list


if __name__ == "__main__":
    data_list = load_tables("1605.08574v1")
