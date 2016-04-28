import tornado.ioloop
import tornado.web
import tornado.escape
import common
import sys, os
import traceback
from itertools import chain
import re

class profListHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		try:
			skip = int(self.get_argument("skip"))
			search = self.get_argument("search", "")
			search = re.sub(r'[^A-Za-z]', ' ', search).split()
			sql = "select * from doge_prof"
			if search:
				sql += " where "
				sql += " and ".join(
						["(school like %s or name like %s)"] * len(search)
						)
				search = ['%' + x + '%' for x in search]
				search = list(chain(*zip(search, search)))
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

class groupListHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		try:
			skip = int(self.get_argument("skip"))
			search = self.get_argument("search", "")
			search = re.sub(r'[^A-Za-z]', ' ', search).split()
			sql = "select * from doge_group"
			if search:
				sql += " where "
				sql += " and ".join(
						["(school like %s or name like %s)"] * len(search)
						)
				search = ['%' + x + '%' for x in search]
				search = list(chain(*zip(search, search)))
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
		r"/(|css/.*|js/.*)",
		tornado.web.StaticFileHandler,
		{
			"path": settings['static_path'],
			"default_filename": "index.html"
			}
		),
	(r"/prof_list", profListHandler),
	(r"/group_list", groupListHandler)
	], **settings)

reload(sys)
sys.setdefaultencoding('utf8')
application.listen(8686)
tornado.ioloop.IOLoop.instance().start()
