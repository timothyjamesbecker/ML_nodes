#!/usr/bin/env python
import argparse
import os
import glob

des = """rename tool: 02/25/2020 Timothy James Becker"""
parser = argparse.ArgumentParser(description=des)
parser.add_argument('-i','--in_dir',type=str,help='input directory\t[None]')
parser.add_argument('-f','--find',type=str,help='pattern to be replaced by prefix\t[None]')
parser.add_argument('-p','--prefix',type=str,help='retrieves prefix from path_to/whatever/prefix.extra.things\t[None]')
parser.add_argument('-e','--exact',type=str,help='exact replacement instead of prefix retrieval\t[None]')
args = parser.parse_args()

if args.exact is None:
    exact = args.exact
    print('replacing pattern=%s with exact=%s'%(args.find,exact))
    for path in sorted(glob.glob(args.in_dir+'/*')):
        if path.find(args.find)>=0:
            new_path = path.replace(args.find,exact)
            os.rename(path,new_path)
elif args.prefix is not None:
    prefix = args.prefix.rsplit('/')[-1].rsplit('.')[0]
    print('replacing pattern=%s with prefix=%s'%(args.find,prefix))
    for path in sorted(glob.glob(args.in_dir+'/*')):
        if path.find(args.find)>=0:
            new_path = path.replace(args.find,prefix)
            os.rename(path,new_path)
