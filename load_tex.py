#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import re
import string
import tarfile
import fnmatch
import requests
import feedparser

__all__ = ["run", "process_file"]

URL = "http://arxiv.org/rss/astro-ph"
COMMENT_RE = re.compile(r"(?<!\\)%")
AMP_RE = re.compile(r"(?<!\\)&")

def run():
    tree = feedparser.parse(URL)
    for entry in tree.entries:
        url = entry.id.replace("/abs/", "/e-print/")
        print(url)


def process_file(fh):
    with tarfile.open(fileobj=fh) as f:
        for mem in f.getmembers():
            if not fnmatch.fnmatch(mem.name, "*.tex"):
                continue
            with f.extractfile(mem) as txtf:
                txt = txtf.read()
            txt = txt.decode("utf-8")

            for line in txt.splitlines():
                groups = COMMENT_RE.findall(line)
                if len(groups):
                    comment = "%".join(line.split("%")[1:]).strip(" \t%")
                    flag = (
                        len(comment) > 0 and
                        len(AMP_RE.findall(comment)) == 0 and
                        comment[0] not in string.punctuation
                    )
                    if flag:
                        print(comment)
    return comment


def load_tex(arxiv_number):
    with open("{0}".format(str(arxiv_number)), "rb") as f:
        text = process_file(f)
    return text


if __name__ == "__main__":
    # load_tex("1605.08574v1")
    with open("1605.08574v1", "rb") as f:
        process_file(f)
