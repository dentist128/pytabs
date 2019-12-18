#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import hashlib
import re
from datetime import datetime

''' command line arguments '''
paramspace = None
''' symbol replacement settings '''
replace_what = None
replace_than = None

''' prepare command line parser '''
def createArgumentParser():
    parser = argparse.ArgumentParser(description="Replace tabs with spaces on python files.")

    parser.add_argument("-r", "--recursive", action="store_true", help="Operate on python (*.py) files on subdirectories recursively.")
    parser.add_argument("-n", "--spaces", default=4, type = int, help="Number of spaces to replace one tab (default: 4).")
    parser.add_argument("-s", "--start-only", action="store_true", help="Replace only at the beginning of the line.")
    parser.add_argument("-t", "--spaces-to-tabs", action="store_true", help="Replace spaces with tabs.")
    parser.add_argument("filename", type=str)

    return parser


''' generate temporary file name '''
def temporaryFileName(filename):
    tmpname = filename + '.new'
    ''' if the file already exists, generate a new name '''
    while os.path.isfile(tmpname):
        tmpname = filename + '.' + hashlib.md5(str(datetime.now()).encode()).hexdigest()[:4]

    return tmpname


''' replace spaces on file '''
def parseFile(filename):
    ''' check file rights '''
    if not os.access(filename, os.W_OK):
        print("No rights for write to '%s'" % filename)

    ''' generate temporary file name '''
    tmpfile = temporaryFileName(filename)

    try:
        ''' replace and store result into temporary file '''
        with open(tmpfile, "w") as file_out:
            with open(filename, "r") as file_in:
                for line in file_in:
                    if paramspace.start_only:
                        for i, c in enumerate(line):
                            if c not in (' ', '\t'):
                                line = line[:i + 1].replace(replace_what, replace_than) + line[i + 1:]
                                break
                    else:
                        line = line.replace(replace_what, replace_than)
                    file_out.write(line)
    except Exception as e:
        print(e)
        return False

    ''' remove original file and move temporary file with original's name '''
    try:
        os.remove(filename)
        os.rename(tmpfile, filename)
    except Exception as e:
        print(e)
        return False

    return True


''' replace spaces on files in directory '''
def parseDir(dirname):
    for root, _, files in os.walk(dirname):
        ''' check parent directory for write rights '''
        if not os.access(root, os.W_OK):
            print("No rights for write on '%s'" % root)
        else:
            ''' filter files by *.py extension '''
            for filename in [ file for file in files if file.endswith('.py') ]:
                ''' parse file '''
                if not parseFile(os.path.abspath('%s/%s' % (root, filename))):
                    return False
    return True


if __name__ == "__main__":
    paramspace = createArgumentParser().parse_args()

    ''' replacement characters setup '''
    replace_what = '\t'
    replace_than = ' ' * paramspace.spaces

    if paramspace.spaces_to_tabs:
        replace_what, replace_than = replace_than, replace_what

    ''' check if file exists '''
    if not os.path.exists(paramspace.filename):
        print("File '%s' does not exists." % paramspace.filename)
        exit(1)

    ''' check if path is a directory or file '''
    if paramspace.recursive:
        if not os.path.isdir(paramspace.filename):
            print("'%s' not a directory." % paramspace.filename)
        else:
            exit(not parseDir(paramspace.filename))
    else:
        if not os.path.isfile(paramspace.filename):
            print("'%s' not a regular file." % paramspace.filename)
        else:
            dirname = os.path.dirname(os.path.abspath(paramspace.filename))
            ''' check parent directory for write rights.
                Because we will create temporary files. '''
            if os.access(dirname, os.W_OK):
                exit(not parseFile(paramspace.filename))
            else:
                print("No rights for write on '%s'" % dirname)

    exit(1)