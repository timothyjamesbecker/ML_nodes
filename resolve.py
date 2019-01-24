#!/usr/bin/env python
import os
import glob
import argparse
parser = argparse.ArgumentParser(description="""wildcard resolution tool""",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-p','--path',type=str,help='search path')
args = parser.parse_args()
if args.path is not None:
    print('\n'.join(glob.glob(os.path.expanduser(args.path))))