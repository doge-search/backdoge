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
	`title` varchar(255) DEFAULT NULL,
	`office` varchar(255) DEFAULT NULL,
	`email` varchar(255) DEFAULT NULL,
	`phone` varchar(255) DEFAULT NULL,
	`website` varchar(255) DEFAULT NULL,
	`image` varchar(255) DEFAULT NULL,
	`group` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8""",
		"doge_group":
"""CREATE TABLE `doge_group` (
	`id` int NOT NULL AUTO_INCREMENT,
	`school` varchar(255) NOT NULL,
	`name` varchar(255) NOT NULL,
	`prof_id` varchar(255) DEFAULT NULL,
	`prof_name` varchar(1023) DEFAULT NULL,
	PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8"""
		}

DB_INSERT_TABLE = {
		"doge_prof": [
			"school", "name", "title", "office", "email",
			"phone", "website", "image", "group"
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
					elem[t] if t in elem else ''
					for t in arg_list
					]
				for elem in params
				]
			)

def init_table(table_name):
	print "Initializing table: %s" % table_name
	db.execute("drop table if exists %s" % table_name)
	db.execute(DB_INIT_TABLE[table_name])
