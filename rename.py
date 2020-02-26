#!/usr/bin/env python
import argparse
import os
import glob

des = """rename tool: 02/25/2020 Timothy James Becker"""
parser = argparse.ArgumentParser(description=des)
parser.add_argument('-i','--in_dir',type=str,help='input directory\t[None]')
parser.add_argument('-f','--find',type=str,help='pattern to be replaced by prefix\t[None]')
parser.add_argument('-p','--prefix',type=str,help='retrieves prefix from path_to/whatever/prefix.extra.things\t[None]')
args = parser.parse_args()

prefix = args.prefix.rsplit('/')[-1].rsplit('.')[0]
print('replacing pattern=%s with prefix=%s'%(args.find,prefix))
for path in sorted(glob.glob(args.in_dir+'/*')):
    if path.find(args.find)>=0:
        new_path = path.replace(args.find,prefix)
        os.rename(path,new_path)
