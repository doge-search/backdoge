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

if args.RESET:
	common.init_table("doge_prof")
	exit(0)

succ_file = open("prof_succ.list", "a")
fail_file = open("prof_fail.list", "a")
succ_sort = open("sort_succ.list", "a")
fail_sort = open("sort_fail.list", "a")

import os
from itertools import izip
for node in os.listdir(args.DIR):
	path = os.path.join(args.DIR, node)
	if not os.path.isdir(path):
		continue
	filename = os.path.join(path, node + ".xml")
	try:
		tree = common.get_tree(succ_file, fail_file, filename)
	except:
		continue
	result = []
	for prof in tree.getroot():
		d = {"school": node, "group": "|"}
		for info in prof:
			d[info.tag] = info.text
		result.append(d)
	filename = os.path.join(path, node + "_sort.xml")
	try:
		tree = common.get_tree(succ_sort, fail_sort, filename)
		for prof_sort, d in izip(tree.getroot(), iter(result)):
			for info in prof_sort:
				if info.tag == 'name':
					if d['name'] != info.text:
						print "Name not matched: %s %s" % \
								(d['name'], info.text)
						raw_input("Enter any key to continue")
						raise Exception("Name not matched: %s %s" % \
								(d['name'], info.text))
				else:
					d[info.tag] = info.text
	except:
		pass
	common.insert_table("doge_prof", result)

succ_file.close()
fail_file.close()
succ_sort.close()
fail_sort.close()
