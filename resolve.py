#!/usr/bin/env python
import argparse
des = """remote wildcard and name resolution testing utility"""
parser = argparse.ArgumentParser(description=des,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-l','--list',type=str,help=', then ; seperated list\t[None]')
args = parser.parse_args()

if args.list is not None:
    L = [x.split(';') for x in args.list.split(',')]
else:
    raise AttributeError

if __name__=='__main__':
    print(L)
