import tornado.ioloop
import tornado.web
import tornado.escape
import common
import sys, os
import traceback
from itertools import chain
import re

class profListHandler(tornado.web.RequestHandler):
	query = {
			"name": "name",
			"school": "school",
			"acm": "`acm-fellow`",
			"ieee": "`ieee-fellow`",
			"nsf": "`nsf-funding`"
			}
	@tornado.web.asynchronous
	def get(self):
		try:
			skip = int(self.get_argument("skip"))
			group = self.get_argument("group", "")
			if group != "":
				sql = "select * from doge_prof where `group` like %s"
				search = ["%|" + group + "|%"]
			else:
				search = self.get_argument("search", "")
				search = re.sub(r'[^A-Za-z:]', ' ', search).split()
				search_sql_list = []
				search_param_list = []
				sql = "select * from doge_prof"
				for i in search:
					pos = i.find(':')
					if pos != -1:
						q = i[:pos]
						if q in self.query: 
							w = i[pos + 1:].replace(":", "")
							if w != "":
								if q in ["acm", "ieee", "nsf"]:
									search_sql_list.append(self.query[q] + "=%s")
									search_param_list.append(str(w[0].lower() != 'n'))
								else:
									search_sql_list.append(self.query[q] + " like %s")
									search_param_list.append('%' + w + '%')
						else:
							search_sql_list.append("(school like %s or name like %s)")
							search_param_list.append('%' + i + '%')
							search_param_list.append('%' + i + '%')
					else:
						search_sql_list.append("(school like %s or name like %s)")
						search_param_list.append('%' + i + '%')
						search_param_list.append('%' + i + '%')
				if search_sql_list:
					sql += " where "
					sql += " and ".join(search_sql_list)
				search = search_param_list
			sql += " order by papers desc limit %d, 11" % skip
			params = [sql] + search
			result = common.db.query(*params)
			for i in result:
				i['papers'] = str(i['papers'])[:6]
			self.write(tornado.escape.json_encode(result))
		except:
			traceback.print_exc()
			pass
		self.finish()

class profGroupHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		try:
			ids = map(lambda x: str(int(x)), self.get_argument("ids").split('|')[1:-1])
			sql = "select name from doge_group where "
			sql += " or ".join(["id=%s"] * len(ids))
			params = [sql] + ids
			result = common.db.query(*params)
			self.write(tornado.escape.json_encode(result))
		except:
			traceback.print_exc()
			pass
		self.finish()

class groupProfHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		try:
			ids = map(lambda x: str(int(x)), self.get_argument("ids").split('|')[1:-1])
			sql = "select name from doge_prof where "
			sql += " or ".join(["id=%s"] * len(ids))
			params = [sql] + ids
			result = common.db.query(*params)
			self.write(tornado.escape.json_encode(result))
		except:
			traceback.print_exc()
			pass
		self.finish()

class groupListHandler(tornado.web.RequestHandler):
	query = {
			"school": "school",
			"group": "name",
			}
	@tornado.web.asynchronous
	def get(self):
		try:
			skip = int(self.get_argument("skip"))
			search = self.get_argument("search", "")
			search = re.sub(r'[^A-Za-z:]', ' ', search).split()
			search_sql_list = []
			search_param_list = []
			sql = "select * from doge_group"
			for i in search:
				pos = i.find(':')
				if pos != -1:
					q = i[:pos]
					if q in self.query: 
						w = i[pos + 1:].replace(":", "")
						if w != "":
							search_sql_list.append(self.query[q] + " like %s")
							search_param_list.append('%' + w + '%')
					else:
						search_sql_list.append("(school like %s or name like %s)")
						search_param_list.append('%' + i + '%')
						search_param_list.append('%' + i + '%')
				else:
					search_sql_list.append("(school like %s or name like %s)")
					search_param_list.append('%' + i + '%')
					search_param_list.append('%' + i + '%')
			if search_sql_list:
				sql += " where "
				sql += " and ".join(search_sql_list)
			search = search_param_list
			sql += " limit %d, 31" % skip
			params = [sql] + search
			result = common.db.query(*params)
			self.write(tornado.escape.json_encode(result))
		except:
			traceback.print_exc()
			pass
		self.finish()

settings = {
		"static_path": os.path.join(
			os.path.dirname(os.path.abspath(__file__)), "frontdoge")
		}

application = tornado.web.Application([
	(
		r"/(|css/.*|js/.*|2/.*)",
		tornado.web.StaticFileHandler,
		{
			"path": settings['static_path'],
			"default_filename": "index.html"
			}
		),
	(r"/prof_list", profListHandler),
	(r"/prof_group", profGroupHandler),
	(r"/group_list", groupListHandler),
	(r"/group_prof", groupProfHandler),
	], **settings)

reload(sys)
sys.setdefaultencoding('utf8')
application.listen(8686)
tornado.ioloop.IOLoop.instance().start()
