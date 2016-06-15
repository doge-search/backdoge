import argparse

parser = argparse.ArgumentParser(
		description = 'Convert professors from XML to MySQL.'
		)
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-a',
		action = 'store',
		dest = 'DIR',
		help = 'append a directory')
group.add_argument('-c',
		action = 'store_true',
		dest = 'RESET',
		help = 'reset database')
args = parser.parse_args()

import common

if args.RESET:
	common.init_table("doge_prof")
	exit(0)

import sys
wd_cont = dict([[y.strip() for y in x.split('\t')]
	for x in open('merge/cont.txt').readlines()])
wd_tree = common.get_tree(
		sys.stderr,
		sys.stderr,
		'merge/professor_2016-06-07_13h35m36.xml'
		)
wd_list = {}
for prof in wd_tree.getroot():
	d = {}
	for info in prof:
		if info.tag == 'name':
			name = info.text.lower()
		elif info.tag == "university":
			for i in info:
				if i.tag == 'name':
					school = i.text
		elif info.tag != "page":
			d[info.tag] = info.text
	if school not in wd_list:
		wd_list[school] = {}
	wd_list[school][name] = d

ssy_list = {}
with open("merge/index.txt") as f:
	for i in f:
		i_split = [x.strip() for x in i.split('|')]
		if len(i_split) == 1:
			continue
		school = i_split[0].split('-')[1]
		if school not in ssy_list:
			ssy_list[school] = {}
		ssy_list[school][i_split[1].lower()] = {
				'acm-fellow': i_split[2],
				'ieee-fellow': i_split[3],
				'nsf-funding': i_split[4]
				}

succ_file = open("prof_succ.list", "a")
fail_file = open("prof_fail.list", "a")
succ_sort = open("sort_succ.list", "a")
fail_sort = open("sort_fail.list", "a")

def check(d, school, name, wd):
	try:
		name_lower = name.lower()
		if name_lower in wd:
			d.update(wd[name_lower])
			return
		name_cont = filter(lambda x: x.isalpha() or x == ' ', name_lower)
		for i in wd:
			if filter(lambda x: x.isalpha() or x == ' ', i) == name_cont:
				d.update(wd[i])
				return
		name_split = name_cont.split()
		for i in wd:
			i_split = filter(lambda x: x.isalpha() or x == ' ', i).split()
			if i_split[0] == name_split[0] and i_split[-1] == name_split[-1]:
				d.update(wd[i])
				return
	except:
		pass
	print "Name not found: %s %s" % (school, name)

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
			if info.tag == 'name':
				check(d, node, info.text, wd_list[wd_cont[node]])
				if node not in ssy_list:
					print "School not found: %s" % node
				else:
					check(d, node, info.text, ssy_list[node])
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
