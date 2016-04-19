import argparse

parser = argparse.ArgumentParser(
		description = 'Convert professors from XML to MySQL.'
		)
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-a',
		action = 'store',
		dest = 'DIR',
		help='append a directory')
group.add_argument('-c',
		action = 'store_true',
		dest = 'RESET',
		help='reset database')
args = parser.parse_args()

import common
from common import db

if args.RESET:
	common.init_table("doge_prof")
	exit(0)

import os
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

for node in os.listdir(args.DIR):
	path = os.path.join(args.DIR, node)
	if not os.path.isdir(path):
		continue
	filename = os.path.join(path, node + ".xml")
	print "Converting %s..." % filename
	try:
		tree = ET.ElementTree(file = filename)
	except IOError:
		print "File %s not found!" % filename
		continue
	result = []
	for prof in tree.getroot():
		d = {"school": node, "group": "|"}
		for info in prof:
			d[info.tag] = info.text
		result.append(d)
	common.insert_table("doge_prof", result)
