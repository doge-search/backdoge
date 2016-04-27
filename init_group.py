import argparse

parser = argparse.ArgumentParser(
		description = 'Convert groups from XML to MySQL.'
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
	common.init_table("doge_group")
	exit(0)

succ_file = open("group_succ.list", "a")
fail_file = open("group_fail.list", "a")

import re

def name_split(name):
	return re.sub(r'[^A-Za-z]', ' ', name).split()

cnt = db.query("select count(*) as cnt from doge_group")[0]["cnt"]

import os
for node in os.listdir(args.DIR):
	path = os.path.join(args.DIR, node)
	if not os.path.isdir(path):
		continue
	filename = os.path.join(path, node + "_research.xml")
	try:
		tree = common.get_tree(succ_file, fail_file, filename)
	except:
		continue
	result = []
	for group in tree.getroot():
		cnt += 1
		d = {"school": node, "prof_id": "|", "prof_name": "|"}
		prof_id = []
		prof_name = []
		for info in group:
			if info.tag == "groupname":
				if info.text:
					d["name"] = info.text
				elif "name" not in d:
					d["name"] = ''
			elif info.tag == "professorname":
				try:
					names = name_split(info.text)
				except:
					continue
				if not names:
					continue
				sql = "select id, school, name from doge_prof where " + \
						(' and '.join(["name like %s"] * len(names)))
				params = [sql] + ['%' + x + '%' for x in names]
				profs = db.query(*params)
				if len(profs) == 1:
					prof_id.append(profs[0]["id"])
					db.update("update doge_prof set `group`=concat(`group`, %s) where id=%s",
							str(cnt) + "|",
							profs[0]["id"])
				elif len(profs) == 0:
					print "\tProfessor not found: %s %s" % (node, info.text)
					prof_name.append(info.text)
				else:
					profs_match = []
					for x in profs:
						name_1 = set([y for y in name_split(x["name"])
								if len(y) > 2])
						name_2 = set([y for y in names
								if len(y) > 2])
						name_s1 = set([y[0] for y in x["name"].split()])
						name_s2 = set([y[0] for y in info.text.split()])
						if (name_1 <= name_2 or name_1 >= name_2) and \
								(name_s1 <= name_s2 or name_s1 >= name_s2):
									profs_match.append(x)
					if len(profs_match) > 0:
						profs = profs_match
						if len(profs) == 1:
							prof_id.append(profs[0]["id"])
							continue
					profs_match = [
							x
							for x in profs
							if x["school"] == node
							]
					if len(profs_match) > 0:
						profs = profs_match
						if len(profs) == 1:
							prof_id.append(profs[0]["id"])
							continue
					print "\tProfessor unable to distinguish: %s %s" % (node, info.text)
					prof_name.append(info.text)
		assert("name" in d)
		d["prof_id"] += ''.join([str(x) + "|" for x in prof_id])
		d["prof_name"] += ''.join([x + "|" for x in prof_name])
		result.append(d)
	common.insert_table("doge_group", result)

succ_file.close()
fail_file.close()
