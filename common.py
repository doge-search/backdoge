import ConfigParser

config = ConfigParser.ConfigParser()
if not config.read('db.cfg'):
	raise Exception("Missing db.cfg")

DB_USERNAME = config.get("mysql", "username")
DB_PASSWORD = config.get("mysql", "password")
DB_DATABASE = config.get("mysql", "database")

import torndb

db = torndb.Connection(
		"localhost",
		DB_DATABASE,
		DB_USERNAME,
		DB_PASSWORD
		)

DB_INIT_TABLE = {
		"doge_prof":
"""CREATE TABLE `doge_prof` (
	`id` int NOT NULL AUTO_INCREMENT,
	`school` varchar(255) NOT NULL,
	`name` varchar(255) NOT NULL,
	`title` varchar(255) NOT NULL,
	`office` varchar(255) NOT NULL,
	`email` varchar(255) NOT NULL,
	`phone` varchar(255) NOT NULL,
	`website` varchar(255) NOT NULL,
	`image` varchar(255) NOT NULL,
	`group` varchar(255) NOT NULL,
	`papers` decimal(20, 15) NOT NULL,
	PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8""",
		"doge_group":
"""CREATE TABLE `doge_group` (
	`id` int NOT NULL AUTO_INCREMENT,
	`school` varchar(255) NOT NULL,
	`name` varchar(255) NOT NULL,
	`prof_id` varchar(1023) NOT NULL,
	`prof_name` varchar(1023) NOT NULL,
	PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8"""
		}

DB_INSERT_TABLE = {
		"doge_prof": [
			"school", "name", "title", "office", "email",
			"phone", "website", "image", "group", "papers"
			],
		"doge_group": [
			"school", "name", "prof_id", "prof_name"
			]
		}

def insert_table(table_name, params):
	arg_list = DB_INSERT_TABLE[table_name]
	sql = "insert into %s (%s) values (%s)" % (
			table_name,
			", ".join(["`%s`" % arg for arg in arg_list]),
			", ".join(["%s"] * len(arg_list))
			)

	db.insertmany(sql,
			[
				[
					elem[t] if (t in elem and elem[t]) else \
							('-1' if t == 'papers' else '')
					for t in arg_list
					]
				for elem in params
				]
			)

def init_table(table_name):
	print "Initializing table: %s" % table_name
	db.execute("drop table if exists %s" % table_name)
	db.execute(DB_INIT_TABLE[table_name])

try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

import traceback
def get_tree(succ_file, fail_file, filename):
	print "Converting %s..." % filename
	while True:
		try:
			tree = ET.ElementTree(file = filename)
			succ_file.write(filename + "\n")
			return tree
		except IOError:
			print "File %s not found!" % filename
			fail_file.write("File %s not found!\n" % filename)
			raise Exception("File %s not found!" % filename)
		except:
			traceback.print_exc()
			if raw_input("Rerun?[Y/n]") != 'Y':
				fail_file.write("Parse %s error!\n" % filename)
				raise Exception("Parse %s error!" % filename)
