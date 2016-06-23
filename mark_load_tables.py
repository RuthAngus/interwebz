#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pdb
import re
import string
import tarfile
import fnmatch
import requests
import feedparser
import numpy as np
import os
import sys
from astropy.table import Table

URL = "http://arxiv.org/rss/astro-ph"
COMMENT_RE = re.compile(r"(?<!\\)%")
AMP_RE = re.compile(r"(?<!\\)&")

DATA_DIR = os.environ.get("ARXIV_DATA_DIR", "data")

def clean_string(tab):
  # First deal with multiple spaces at front of line
  tab = tab.expandtabs()
  tab = re.sub("\\\\hline","",tab)
  tab = re.sub("\$","",tab)
  tab = re.sub(" *\n","\n",tab)
  tab = re.sub("(?<!\\\\\\\\)\n","",tab)
  tab = re.sub("(?<!\n) *\\\\caption","\n\\\\caption",tab)
  tab = re.sub("(?<!\n) *\\\\centering","\n\\\\centering",tab)
  tab = re.sub("(?<!\n) *\\\\label","\n\\\\label",tab)
  tab = re.sub("(?<!\n) *\\\\item","\n\\\\item",tab)
  tab = re.sub("(?<!\n) *\\\\begin","\n\\\\begin",tab)
  tab = re.sub("(?<=[lcr])r}(?!\n)","r}\n",tab)
  tab = re.sub("(?<=[lcr])l}(?!\n)","l}\n",tab)
  tab = re.sub("(?<=[lcr])c}(?!\n)","c}\n",tab)
  tab = re.sub("(?<!\n) *\\\\end","\n\\\\end",tab)
  tab = re.sub("\n  *","\n",tab)
  tab = re.sub("^\n","",tab)
  tab = re.sub("\n\n*","\n",tab)
  return tab


def split_errors(table):
    # Here we find string columns with \pm and split them into new columns
    repl_str = np.str_("\pm")
    for col_name in table.colnames:
        if type(table[col_name][0]) == type(np.str_()) :
            do_split = False
            for entry in table[col_name]:
                if entry.find(repl_str) >= 0:
                    do_split = True
                    break
            if do_split :
                new_col_name = col_name + "Data"
                new_col_error_name = new_col_name + "Err"
                table[new_col_name] = np.zeros(len(table[col_name]),dtype=np.float64)
                table[new_col_error_name] = np.zeros(len(table[col_name]),dtype=np.float64)
                new_index = 0
                for entry in table[col_name]:
                    if entry.find(repl_str) < 0:
                        try:
                            new_data = np.float64(entry)
                        except:
                            new_data = np.nan
                        new_error = np.nan
                    else:
                        new_entry = (entry.replace(repl_str,np.str_(" "))).split()
                        new_data = np.float64(new_entry[0])
                        new_error = np.float64(new_entry[1])
                    table[new_col_name][new_index] = new_data
                    table[new_col_error_name][new_index] = new_error
                    new_index = new_index + 1
                table.remove_column(col_name)
    return table

def run():
    tree = feedparser.parse(URL)
    for entry in tree.entries:
        url = entry.id.replace("/abs/", "/e-print/")
        print(url)

def extract_tables_other(fh):

    with tarfile.open(fileobj=fh) as f:
        for mem in f.getmembers():
            if not fnmatch.fnmatch(mem.name, "*.tex"):
                continue
            txtf = f.extractfile(mem)
#            print(type(txtf))
            txt = txtf.read()
            txtf.close()
            txt = txt.decode("utf-8")

            tables = []

            # table
            ind1 = 0
            ind2 = 0
            while ind1 >= 0:
                ind1 = txt.find(r'\begin{table}',0+ind1+1)
                ind2 = txt.find(r'\end{table}',0+ind2+1)
                print(ind1, ind2)

                if ind2 > 0:
                    tab = txt[ind1:ind2+len(r'\end{table}')+1]
        #            pdb.set_trace()
                    tab = clean_string(tab)
                    #print(tab)
        #            pdb.set_trace()
                    f = open("temp.tex",'w')
                    f.write(tab)
                    f.close()

                    #pdb.set_trace()
                    tex_tab = Table.read("temp.tex",format='latex',guess=False)
                    os.remove("temp.tex")
        #            pdb.set_trace()
                    tex_tab = split_errors(tex_tab)
        #            pdb.set_trace()
                    tables.append(tex_tab)
                    if len(tables) == 2:
                        break

            # table
            ind1 = -1
            ind2 = 0
            while ind1 >= 0:
                ind1 = txt.find(r'\begin{deluxetable}',0+ind1+1)
                ind2 = txt.find(r'\end{deluxetable}',0+ind2+1)
                print(ind1, ind2)

                if ind2 > 0:
                    tab = txt[ind1:ind2+len(r'\end{deluxetable}')+1]
                    tab = clean_string(tab)
                    #print(tab)
                    pdb.set_trace()
                    f = open("temp.tex",'w')
                    f.write(tab)
                    f.close()

                    #pdb.set_trace()
                    tex_tab = Table.read("temp.tex",format='ascii.aastex',guess=False)
                    os.remove("temp.tex")
                    tex_tab = split_errors(tex_tab)
                    tables.append(tex_tab)

            # table
            ind1 = -1
            ind2 = 0
            while ind1 >= 0:
                ind1 = txt.find(r'\begin{table*}',0+ind1+1)
                ind2 = txt.find(r'\end{table*}',0+ind2+1)
                print(ind1, ind2)

                if ind2 > 0:
                    tab = txt[ind1:ind2+len(r'\end{table*}')+1]
                    tab = clean_string(tab)
                    #print(tab)
                    pdb.set_trace()
                    f = open("temp.tex",'w')
                    f.write(tab)
                    f.close()

                    #pdb.set_trace()
                    tex_tab = Table.read("temp.tex",format='latex')
                    os.remove("temp.tex")
                    tex_tab = split_errors(tex_tab)
                    tables.append(tex_tab)

            # table
            ind1 = -1
            ind2 = 0
            while ind1 >= 0:
                ind1 = txt.find(r'\begin{deluxetable*}',0+ind1+1)
                ind2 = txt.find(r'\end{deluxetable*}',0+ind2+1)
                print(ind1, ind2)

                if ind2 > 0:
                    tab = txt[ind1:ind2+len(r'\end{deluxetable*}')+1]
                    tab = clean_string(tab)
                    #print(tab)
                    pdb.set_trace()
                    f = open("temp.tex",'w')
                    f.write(tab)
                    f.close()

                    #pdb.set_trace()
                    tex_tab = Table.read("temp.tex",format='ascii.aastex',guess=False)
                    os.remove("temp.tex")
                    tex_tab = split_errors(tex_tab)
                    tables.append(tex_tab)

            return tables



#    pdb.set_trace()

def extract_tables(fh):
    """
    Extracts tables from latex file and returns a list of strings.
    One string for each table.
    """
    with tarfile.open(mode="r:gz",fileobj=fh) as f:
        for mem in f.getmembers():
            if not fnmatch.fnmatch(mem.name, "*.tex"):
                continue
            #with f.extractfile(mem) as txtf:
            txtf = f.extractfile(mem)
#            print(type(txtf))
            txt = txtf.read()
            txtf.close()
            txt = txt.decode("utf-8")

            # detect table line positions
            tables = []
            lines = np.array(txt.splitlines())
            for i, line in enumerate(lines):
                if line[1:12] == "begin{table" or \
                        line[1:18] == "begin{deluxetable":
                    beg_ind = i
                elif line[1:10] == "end{table" or \
                    line[1:16] == "end{deluxetable":
                    end_ind = i
#                    pdb.set_trace()
                    tables.append(lines[beg_ind:end_ind])
    return tables

def read_table_other(table):
    head = table.colnames
    data = np.zeros([len(table[table.colnames[0]]),len(table.colnames)])
    i=0
    for colname in table.colnames:
        j=0
        for entry in table[colname]:
            try:
                data[j,i] = np.float64(entry)
            except:
                data[j,i] = np.nan
            j = j + 1
        i = i + 1
    units = ['unit']*len(head)
    return head, data, units

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
    file = os.path.join(DATA_DIR, "{0}.tar.gz".format(str(arxiv_number)))
    with open(file, "rb") as f:
        tables = extract_tables_other(f)
    data_list, header_list, unit_list = [], [], []
    for table in tables:
        dat, head, unit = read_table_other(table)
        data_list.append(dat)
        header_list.append(head)
        unit_list.append(unit)
    return data_list, header_list, unit_list


if __name__ == "__main__":
    # data_list = load_tables("1605.08574v1")
    aid = "1606.01926v1"
    if len(sys.argv) > 1:
        aid = sys.argv[1]
    data_list, header_list, unit_list = \
        data_list = load_tables(aid)
    print(data_list)
