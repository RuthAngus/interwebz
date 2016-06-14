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
    print(fh)
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
    """
    for i, line in enumerate(table):
        # if line.find("begin{tabular}"):
        if "begin{tabular}" in line:
            start = i + 1
        elif "end{tabular}" in line:
            end = i
    just_data = table[start:end]
    header = just_data[0]
    print(header)
    input("")


def load_tables(arxiv_number):
    """
    Takes an ArXiv id and returns a list of arrays.
    Each array contains the data in a table in the paper.
    """
    with open("{0}".format(str(arxiv_number)), "rb") as f:
        tables = extract_tables(f)
    data_list = []
    for table in tables:
        data_list.append(read_table(table))
    return data_list


if __name__ == "__main__":
    load_tables("1605.08574v1")
